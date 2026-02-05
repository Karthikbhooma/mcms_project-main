"""
End-to-End Integration Tests for MCMS
Tests core user flows: registration, login, complaint submission, AJAX category loading
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO

from accounts.models import Citizen
from departments.models import Department, ComplaintCategory
from complaints.models import Complaint


class UserAuthenticationTests(TestCase):
    """Test user registration and login flows"""
    
    def setUp(self):
        self.client = Client()
        self.username = 'testcitizen'
        self.email = 'test@example.com'
        self.mobile = '9876543210'
        self.password = 'SecurePass123!'
    
    def test_user_creation(self):
        """Test creating a new citizen user"""
        user = Citizen.objects.create_user(
            username=self.username,
            email=self.email,
            mobile=self.mobile,
            password=self.password
        )
        self.assertTrue(user)
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertFalse(user.is_verified)  # Should not be verified by default
    
    def test_user_login(self):
        """Test logging in a citizen"""
        user = Citizen.objects.create_user(
            username=self.username,
            email=self.email,
            mobile=self.mobile,
            password=self.password
        )
        user.is_verified = True
        user.save()
        
        login_success = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login_success)
    
    def test_login_page_loads(self):
        """Test that login page renders"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Citizen Login', response.content)
    
    def test_register_page_loads(self):
        """Test that registration page renders"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Citizen Registration', response.content)


class DepartmentAndCategoryTests(TestCase):
    """Test department and category views"""
    
    def setUp(self):
        self.dept_code = 'WATER_SUPPLY'
        self.dept = Department.objects.create(
            code=self.dept_code,
            name='Water Supply',
            description='Water supply and distribution department'
        )
        self.category = ComplaintCategory.objects.create(
            department=self.dept,
            name='Pipe Leakage',
            description='Water pipe leakage issues',
            is_active=True
        )
    
    def test_department_list_page(self):
        """Test department list page loads"""
        response = self.client.get(reverse('departments:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Water Supply', response.content)
    
    def test_department_detail_page(self):
        """Test department detail page loads"""
        response = self.client.get(reverse('departments:detail', args=[self.dept_code]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Water Supply', response.content)
        self.assertIn(b'Pipe Leakage', response.content)
    
    def test_ajax_load_categories(self):
        """Test AJAX endpoint loads categories for a department"""
        response = self.client.get(
            reverse('complaints:ajax_load_categories'),
            {'department_id': self.dept_code}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('categories', data)
        self.assertTrue(len(data['categories']) > 0)
        self.assertEqual(data['categories'][0]['name'], 'Pipe Leakage')


class ComplaintSubmissionTests(TestCase):
    """Test complaint submission flow"""
    
    def setUp(self):
        self.client = Client()
        
        # Create user
        self.user = Citizen.objects.create_user(
            username='complainant',
            email='complainant@example.com',
            mobile='9111111111',
            password='TestPass123!'
        )
        self.user.is_verified = True
        self.user.save()
        
        # Create department
        self.dept = Department.objects.create(
            code='ROADS_TRANSPORT',
            name='Roads & Transport',
            description='Road maintenance and transport'
        )
        
        # Create category
        self.category = ComplaintCategory.objects.create(
            department=self.dept,
            name='Pothole',
            description='Road potholes',
            is_active=True
        )
    
    def test_submit_complaint_page_loads(self):
        """Test complaint submit page loads for logged-in user"""
        self.client.login(username='complainant', password='TestPass123!')
        response = self.client.get(reverse('complaints:submit'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'File New Complaint', response.content)
    
    def test_submit_complaint_with_file(self):
        """Test submitting a complaint with file upload"""
        self.client.login(username='complainant', password='TestPass123!')
        
        # Create a test file
        file_content = b'Test PDF content for proof'
        uploaded_file = SimpleUploadedFile(
            'pothole_proof.pdf',
            file_content,
            content_type='application/pdf'
        )
        
        complaint_data = {
            'department': self.dept.code,
            'category': self.category.id,
            'ward_number': '15',
            'area': 'Market Square',
            'landmark': 'Near Clock Tower',
            'subject': 'Large pothole on Main Street',
            'description': 'There is a large pothole on Main Street causing traffic issues and vehicle damage. Needs urgent repair.',
            'proof_file': uploaded_file
        }
        
        response = self.client.post(
            reverse('complaints:submit'),
            complaint_data,
            follow=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Verify complaint was created
        complaint = Complaint.objects.filter(
            subject='Large pothole on Main Street'
        ).first()
        
        self.assertIsNotNone(complaint)
        self.assertEqual(complaint.citizen, self.user)
        self.assertEqual(complaint.department, self.dept)
        self.assertEqual(complaint.area, 'Market Square')
        self.assertTrue(complaint.proof_file)
    
    def test_submit_complaint_without_file(self):
        """Test submitting a complaint without proof file"""
        self.client.login(username='complainant', password='TestPass123!')
        
        complaint_data = {
            'department': self.dept.code,
            'ward_number': '10',
            'area': 'Residential Zone',
            'subject': 'Street light not working',
            'description': 'The street light on 5th Avenue has been non-functional for a week. Needs immediate attention.',
        }
        
        response = self.client.post(
            reverse('complaints:submit'),
            complaint_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify complaint was created
        complaint = Complaint.objects.filter(
            subject='Street light not working'
        ).first()
        
        self.assertIsNotNone(complaint)
        self.assertEqual(complaint.citizen, self.user)


class ComplaintDashboardTests(TestCase):
    """Test complaint dashboard and tracking"""
    
    def setUp(self):
        self.client = Client()
        
        # Create user
        self.user = Citizen.objects.create_user(
            username='dashboard_user',
            email='dashboard@example.com',
            mobile='9222222222',
            password='TestPass123!'
        )
        self.user.is_verified = True
        self.user.save()
        
        # Create department and complaint
        self.dept = Department.objects.create(
            code='SANITATION',
            name='Sanitation',
            description='Sanitation services'
        )
        
        self.complaint = Complaint.objects.create(
            citizen=self.user,
            department=self.dept,
            subject='Garbage collection pending',
            description='Garbage has not been collected for 3 days',
            ward_number='8',
            area='Downtown',
            status='SUBMITTED'
        )
    
    def test_dashboard_loads(self):
        """Test complaint dashboard loads for logged-in user"""
        self.client.login(username='dashboard_user', password='TestPass123!')
        response = self.client.get(reverse('complaints:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Garbage collection pending', response.content)
    
    def test_complaint_detail_page(self):
        """Test viewing complaint details"""
        self.client.login(username='dashboard_user', password='TestPass123!')
        response = self.client.get(
            reverse('complaints:detail', args=[self.complaint.complaint_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Garbage collection pending', response.content)
    
    def test_track_complaint(self):
        """Test tracking a complaint by ID"""
        self.client.login(username='dashboard_user', password='TestPass123!')
        response = self.client.get(
            reverse('complaints:track'),
            {'complaint_id': self.complaint.complaint_id}
        )
        self.assertEqual(response.status_code, 200)


class TemplateRenderingTests(TestCase):
    """Test all key templates render without errors"""
    
    def setUp(self):
        self.client = Client()
        self.user = Citizen.objects.create_user(
            username='renderer',
            email='render@example.com',
            mobile='9333333333',
            password='TestPass123!'
        )
        self.user.is_verified = True
        self.user.save()
    
    def test_home_page_renders(self):
        """Test home page renders"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_departments_list_renders(self):
        """Test departments list renders"""
        response = self.client.get(reverse('departments:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_page_renders(self):
        """Test login page renders"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_page_renders(self):
        """Test register page renders"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
    
    def test_authenticated_pages_redirect_anonymous(self):
        """Test that protected pages redirect anonymous users"""
        response = self.client.get(reverse('complaints:dashboard'), follow=False)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_authenticated_pages_load_for_users(self):
        """Test that protected pages load for authenticated users"""
        self.client.login(username='renderer', password='TestPass123!')
        response = self.client.get(reverse('complaints:dashboard'))
        self.assertEqual(response.status_code, 200)
