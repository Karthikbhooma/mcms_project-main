"""
Admin Panel Views
Municipal officer dashboard and complaint management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.mail import send_mail
from complaints.models import Complaint, ComplaintStatusHistory
from departments.models import Department
from .forms import AdminLoginForm, UpdateComplaintStatusForm


def is_admin_user(user):
    """Check if user is staff/admin"""
    return user.is_authenticated and user.is_staff


def admin_login_view(request):
    """
    Admin login page
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('adminpanel:dashboard')
    
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('adminpanel:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    else:
        form = AdminLoginForm()
    
    context = {'form': form}
    return render(request, 'adminpanel/login.html', context)


@login_required
@user_passes_test(is_admin_user, login_url='/admin-panel/login/')
def admin_dashboard(request):
    """
    Admin dashboard with statistics
    """
    # Overall statistics
    total_complaints = Complaint.objects.filter(is_archived=False).count()
    pending_complaints = Complaint.objects.filter(
        is_archived=False
    ).exclude(status__in=['RESOLVED', 'CLOSED']).count()
    resolved_complaints = Complaint.objects.filter(
        status__in=['RESOLVED', 'CLOSED'],
        is_archived=False
    ).count()
    
    # Status-wise breakdown
    status_stats = Complaint.objects.filter(is_archived=False).values('status').annotate(
        count=Count('id')
    )
    
    # Department-wise statistics
    dept_stats = Department.objects.annotate(
        total=Count('complaints', filter=Q(complaints__is_archived=False)),
        pending=Count('complaints', filter=Q(
            complaints__is_archived=False,
            complaints__status__in=['SUBMITTED', 'UNDER_REVIEW', 'IN_PROGRESS']
        )),
        resolved=Count('complaints', filter=Q(
            complaints__is_archived=False,
            complaints__status__in=['RESOLVED', 'CLOSED']
        ))
    )
    
    # Recent complaints
    recent_complaints = Complaint.objects.filter(
        is_archived=False
    ).select_related('citizen', 'department', 'officer')[:10]
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'status_stats': status_stats,
        'dept_stats': dept_stats,
        'recent_complaints': recent_complaints,
    }
    return render(request, 'adminpanel/dashboard.html', context)


@login_required
@user_passes_test(is_admin_user, login_url='/admin-panel/login/')
def all_complaints(request):
    """
    View all complaints with filters
    """
    complaints = Complaint.objects.filter(
        is_archived=False
    ).select_related('citizen', 'department', 'officer')
    
    # Filters
    status_filter = request.GET.get('status', '')
    dept_filter = request.GET.get('department', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    if dept_filter:
        complaints = complaints.filter(department__code=dept_filter)
    
    if search:
        complaints = complaints.filter(
            Q(complaint_id__icontains=search) |
            Q(subject__icontains=search) |
            Q(citizen__username__icontains=search)
        )
    
    # Order by submission date (newest first)
    complaints = complaints.order_by('-submitted_at')
    
    # Get all departments for filter
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'complaints': complaints,
        'departments': departments,
        'status_choices': Complaint.STATUS_CHOICES,
        'current_status': status_filter,
        'current_dept': dept_filter,
        'search_query': search,
    }
    return render(request, 'adminpanel/all_complaints.html', context)


@login_required
@user_passes_test(is_admin_user, login_url='/admin-panel/login/')
def complaint_detail_admin(request, complaint_id):
    """
    View and update complaint details (Admin)
    """
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    
    if request.method == 'POST':
        form = UpdateComplaintStatusForm(request.POST, request.FILES, instance=complaint)
        
        if form.is_valid():
            old_status = complaint.status
            new_complaint = form.save(commit=False)
            new_status = new_complaint.status
            
            # Update timestamp based on status
            if new_status == 'UNDER_REVIEW' and not complaint.reviewed_at:
                new_complaint.reviewed_at = timezone.now()
            elif new_status == 'IN_PROGRESS' and not complaint.in_progress_at:
                new_complaint.in_progress_at = timezone.now()
            elif new_status == 'RESOLVED' and not complaint.resolved_at:
                new_complaint.resolved_at = timezone.now()
            elif new_status == 'CLOSED' and not complaint.closed_at:
                new_complaint.closed_at = timezone.now()
            
            new_complaint.save()

            # If resolution proof uploaded, ensure file saved on instance
            if form.cleaned_data.get('resolution_proof'):
                # saved via ModelForm save(); nothing extra required
                pass
            
            # Create status history entry
            if old_status != new_status:
                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    from_status=old_status,
                    to_status=new_status,
                    changed_by=request.user,
                    remarks=form.cleaned_data.get('official_remarks', '')
                )

            # If moved to RESOLVED, send notification to citizen with resolution notes
            if new_status == 'RESOLVED':
                try:
                    subject = f"Your complaint {complaint.complaint_id} is Resolved"
                    message_lines = [
                        f"Hello {complaint.citizen.username},",
                        "\n",
                        f"Your complaint ({complaint.complaint_id}) has been marked as RESOLVED.",
                    ]
                    res_notes = form.cleaned_data.get('resolution_notes')
                    if res_notes:
                        message_lines += ["\nResolution details:", res_notes]

                    # Official remarks visible to citizen
                    official = form.cleaned_data.get('official_remarks')
                    if official:
                        message_lines += ["\nOfficial remarks:", official]

                    message = "\n".join(message_lines)
                    send_mail(
                        subject,
                        message,
                        None,
                        [complaint.citizen.email],
                        fail_silently=True,
                    )
                except Exception:
                    # do not block admin action if email fails
                    pass
            
            messages.success(request, 'Complaint updated successfully!')
            return redirect('adminpanel:complaint_detail', complaint_id=complaint_id)
    else:
        form = UpdateComplaintStatusForm(instance=complaint)
    
    # Get status history
    status_history = complaint.status_history.all()
    
    context = {
        'complaint': complaint,
        'form': form,
        'status_history': status_history,
    }
    return render(request, 'adminpanel/complaint_detail.html', context)


@login_required
@user_passes_test(is_admin_user, login_url='/admin-panel/login/')
def resolve_complaint(request, complaint_id):
    """Quick resolve action for admin: sets status to RESOLVED with optional notes/proof"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id, is_archived=False)
    if request.method == 'POST':
        notes = request.POST.get('resolution_notes', '')
        official = request.POST.get('official_remarks', '')
        proof = request.FILES.get('resolution_proof')

        old_status = complaint.status
        complaint.status = 'RESOLVED'
        if not complaint.resolved_at:
            complaint.resolved_at = timezone.now()
        if notes:
            complaint.resolution_notes = notes
        if official:
            complaint.official_remarks = official
        if proof:
            complaint.resolution_proof = proof
        complaint.save()

        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            from_status=old_status,
            to_status='RESOLVED',
            changed_by=request.user,
            remarks=official or notes,
        )

        # notify citizen
        try:
            send_mail(
                f"Your complaint {complaint.complaint_id} is Resolved",
                f"Hello {complaint.citizen.username},\n\nYour complaint has been marked as RESOLVED.\n\nResolution notes:\n{complaint.resolution_notes or '—'}\n\nOfficial remarks:\n{complaint.official_remarks or '—'}",
                None,
                [complaint.citizen.email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'Complaint marked as RESOLVED.')
    return redirect('adminpanel:complaint_detail', complaint_id=complaint_id)


@login_required
@user_passes_test(is_admin_user, login_url='/admin-panel/login/')
def delete_complaint(request, complaint_id):
    """Soft-delete (archive) a complaint."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if request.method == 'POST':
        complaint.is_archived = True
        complaint.save()
        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            from_status=complaint.status,
            to_status='ARCHIVED',
            changed_by=request.user,
            remarks='Complaint archived by admin'
        )
        messages.success(request, 'Complaint archived (deleted) successfully.')
    return redirect('adminpanel:all_complaints')


@login_required
@user_passes_test(is_admin_user, login_url='/admin-panel/login/')
def department_complaints(request, dept_code):
    """
    View complaints by department
    """
    department = get_object_or_404(Department, code=dept_code)
    
    complaints = Complaint.objects.filter(
        department=department,
        is_archived=False
    ).select_related('citizen', 'officer').order_by('-submitted_at')
    
    # Statistics for this department
    total = complaints.count()
    pending = complaints.exclude(status__in=['RESOLVED', 'CLOSED']).count()
    resolved = complaints.filter(status__in=['RESOLVED', 'CLOSED']).count()
    
    context = {
        'department': department,
        'complaints': complaints,
        'total': total,
        'pending': pending,
        'resolved': resolved,
    }
    return render(request, 'adminpanel/department_complaints.html', context)


@login_required
@user_passes_test(is_admin_user, login_url='/admin-panel/login/')
def reports(request):
    """
    Reports and analytics page
    """
    # Date range filter (optional enhancement)
    from datetime import datetime, timedelta
    
    # Last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Recent complaints
    recent_complaints = Complaint.objects.filter(
        submitted_at__gte=thirty_days_ago,
        is_archived=False
    ).count()
    
    # Department-wise detailed stats
    dept_stats = Department.objects.annotate(
        total=Count('complaints', filter=Q(complaints__is_archived=False)),
        submitted=Count('complaints', filter=Q(
            complaints__status='SUBMITTED',
            complaints__is_archived=False
        )),
        under_review=Count('complaints', filter=Q(
            complaints__status='UNDER_REVIEW',
            complaints__is_archived=False
        )),
        in_progress=Count('complaints', filter=Q(
            complaints__status='IN_PROGRESS',
            complaints__is_archived=False
        )),
        resolved=Count('complaints', filter=Q(
            complaints__status='RESOLVED',
            complaints__is_archived=False
        )),
        closed=Count('complaints', filter=Q(
            complaints__status='CLOSED',
            complaints__is_archived=False
        ))
    )
    
    context = {
        'recent_complaints_count': recent_complaints,
        'dept_stats': dept_stats,
    }
    return render(request, 'adminpanel/reports.html', context)


@login_required
@user_passes_test(is_admin_user, login_url='/admin-panel/login/')
def admin_logout(request):
    """
    Admin logout
    """
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('adminpanel:login')
