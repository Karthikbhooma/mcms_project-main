"""
Complaints Views
Citizen complaint submission and tracking
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Complaint, ComplaintStatusHistory
from .forms import ComplaintForm
    


@login_required
def citizen_dashboard(request):
    """
    Citizen dashboard - view all submitted complaints
    """
    complaints = Complaint.objects.filter(
        citizen=request.user,
        is_archived=False
    ).select_related('department')
    
    # Statistics
    total_complaints = complaints.count()
    pending_complaints = complaints.exclude(status__in=['RESOLVED', 'CLOSED']).count()
    resolved_complaints = complaints.filter(status__in=['RESOLVED', 'CLOSED']).count()
    
    context = {
        'complaints': complaints,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
    }
    return render(request, 'complaints/dashboard.html', context)


@login_required
def submit_complaint(request):
    """
    Submit new complaint
    """
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.citizen = request.user
            complaint.status = 'SUBMITTED'
            complaint.save()
            
            # Create initial status history
            ComplaintStatusHistory.objects.create(
                complaint=complaint,
                from_status='',
                to_status='SUBMITTED',
                changed_by=request.user,
                remarks='Complaint submitted by citizen'
            )
            
            messages.success(
                request,
                f'Complaint submitted successfully! Your Complaint ID: {complaint.complaint_id}'
            )
            return redirect('complaints:detail', complaint_id=complaint.complaint_id)
    else:
        form = ComplaintForm()
    
    context = {
        'form': form
    }
    return render(request, 'complaints/submit.html', context)


@login_required
def complaint_detail(request, complaint_id):
    """
    View complaint details and history
    """
    complaint = get_object_or_404(
        Complaint,
        complaint_id=complaint_id,
        citizen=request.user
    )
    
    # Get status history
    status_history = complaint.status_history.all()
    
    context = {
        'complaint': complaint,
        'status_history': status_history,
    }
    return render(request, 'complaints/detail.html', context)


@login_required
def track_complaint(request):
    """
    Track complaint by ID
    """
    complaint_id = request.GET.get('complaint_id', '').strip()
    complaint = None
    
    if complaint_id:
        try:
            complaint = Complaint.objects.get(
                complaint_id=complaint_id,
                citizen=request.user
            )
        except Complaint.DoesNotExist:
            messages.error(request, 'Complaint not found or you do not have permission to view it.')
    
    context = {
        'complaint': complaint,
        'search_id': complaint_id
    }
    return render(request, 'complaints/track.html', context)


    
