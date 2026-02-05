"""
Departments Views
Display department information
"""

from django.shortcuts import render, get_object_or_404
from .models import Department, ComplaintCategory


def department_list(request):
    """
    List all active departments
    """
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'departments': departments
    }
    return render(request, 'departments/list.html', context)


def department_detail(request, dept_code):
    """
    Department detail page with categories
    """
    department = get_object_or_404(Department, code=dept_code, is_active=True)
    categories = department.categories.filter(is_active=True)
    
    context = {
        'department': department,
        'categories': categories
    }
    return render(request, 'departments/detail.html', context)
