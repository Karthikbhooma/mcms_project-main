"""
Departments Models
Municipal department structure for complaint categorization
"""

from django.db import models


class Department(models.Model):
    """
    Municipal Department Model
    Represents different civic service departments
    """
    
    DEPARTMENT_CHOICES = [
        ('WATER_SUPPLY', 'Water Supply'),
        ('ROADS_TRANSPORT', 'Roads & Transport'),
        ('SANITATION', 'Sanitation'),
        ('ELECTRICITY', 'Electricity'),
        ('PUBLIC_HEALTH', 'Public Health'),
    ]
    
    code = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        unique=True,
        primary_key=True
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    head_of_department = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_complaint_count(self):
        """Get total complaints for this department"""
        return self.complaints.count()
    
    def get_pending_count(self):
        """Get pending complaints count"""
        return self.complaints.exclude(status__in=['RESOLVED', 'CLOSED']).count()
    
    def get_resolved_count(self):
        """Get resolved complaints count"""
        return self.complaints.filter(status__in=['RESOLVED', 'CLOSED']).count()


class ComplaintCategory(models.Model):
    """
    Complaint Category Model
    Specific categories under each department
    """
    
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=1)  # 1=Low, 2=Medium, 3=High
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'complaint_categories'
        verbose_name = 'Complaint Category'
        verbose_name_plural = 'Complaint Categories'
        ordering = ['department', 'name']
        unique_together = ['department', 'name']
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"
