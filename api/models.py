from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Academic Year
class AcademicYear(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


# Semester
class Semester(models.Model):
    SEMESTER_CHOICES = [
        ('1ST', 'First Semester'),
        ('2ND', 'Second Semester'),
        ('SUMMER', 'Summer'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    semester_type = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    enrollment_start = models.DateField()
    enrollment_end = models.DateField()

    class Meta:
        unique_together = ('academic_year', 'semester_type')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.get_semester_type_display()} - {self.academic_year.name}"


# Department
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    building = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


# Faculty
class Faculty(models.Model):
    EMPLOYMENT_STATUS = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='faculty')
    employee_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=50, blank=True)  # e.g. "Professor", "Lecturer"
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='FULL_TIME')
    specialization = models.TextField(blank=True)
    office_room = models.CharField(max_length=50, blank=True)
    consultation_hours = models.TextField(blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    date_hired = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Faculty"
        ordering = ['user__last_name']

    def __str__(self):
        return f"{self.title} {self.user.get_full_name()}"


# Student
class Student(models.Model):
    YEAR_LEVEL_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
        (5, 'Fifth Year'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('GRADUATED', 'Graduated'),
        ('SUSPENDED', 'Suspended'),
        ('LOA', 'Leave of Absence'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='students')
    date_of_birth = models.DateField(null=True, blank=True)
    year_level = models.IntegerField(choices=YEAR_LEVEL_CHOICES, default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=15, blank=True)
    enrolled_at = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"


# Program
class Program(models.Model):
    DEGREE_CHOICES = [
        ('BS', 'Bachelor of Science'),
        ('BA', 'Bachelor of Arts'),
        ('MS', 'Master of Science'),
        ('MA', 'Master of Arts'),
        ('PHD', 'Doctor of Philosophy'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    degree_type = models.CharField(max_length=10, choices=DEGREE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    description = models.TextField(blank=True)
    total_units = models.PositiveIntegerField(default=120)
    duration_years = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.code} - {self.name}"

# Course
class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ('MAJOR', 'Major'),
        ('MINOR', 'Minor'),
        ('GEN_ED', 'General Education'),
        ('ELECTIVE', 'Elective'),
    ]
    
    course_code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='courses')
    units = models.PositiveIntegerField(default=3)
    lecture_hours = models.PositiveIntegerField(default=3)
    lab_hours = models.PositiveIntegerField(default=0)
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='MAJOR')
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='prerequisite_for')
    year_level = models.IntegerField(default=1)
    semester_offered = models.CharField(max_length=10, blank=True)  # "1ST", "2ND", "BOTH"

    class Meta:
        ordering = ['course_code']

    def __str__(self):
        return f"{self.course_code} - {self.title}"


# Course Offering (Section)
class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='course_offerings')
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='course_offerings')
    section = models.CharField(max_length=10)  # e.g., "A", "B", "C"
    max_slots = models.PositiveIntegerField(default=40)
    enrolled_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('course', 'semester', 'section')
        ordering = ['course', 'section']

    def __str__(self):
        return f"{self.course.course_code} - {self.section} ({self.semester})"

    @property
    def available_slots(self):
        return self.max_slots - self.enrolled_count


# Schedule
class Schedule(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]
    
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    building = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.course_offering} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


# Enrollment
class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('ENROLLED', 'Enrolled'),
        ('DROPPED', 'Dropped'),
        ('COMPLETED', 'Completed'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    dropped_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course_offering')
        ordering = ['-date_enrolled']

    def __str__(self):
        return f"{self.student.student_id} enrolled in {self.course_offering}"


# Grade
class Grade(models.Model):
    GRADE_CHOICES = [
        ('1.00', '1.00'),
        ('1.25', '1.25'),
        ('1.50', '1.50'),
        ('1.75', '1.75'),
        ('2.00', '2.00'),
        ('2.25', '2.25'),
        ('2.50', '2.50'),
        ('2.75', '2.75'),
        ('3.00', '3.00'),
        ('5.00', '5.00 (Failed)'),
        ('INC', 'Incomplete'),
        ('DRP', 'Dropped'),
    ]
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='grade')
    midterm_grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    final_grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    final_rating = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True)
    remarks = models.CharField(max_length=50, blank=True)  # e.g., "Passed", "Failed"
    date_submitted = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.enrollment.course_offering.course.course_code} - {self.final_rating}"



# Announcement
class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    target_audience = models.CharField(max_length=50, default='ALL')  # ALL, STUDENTS, FACULTY
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='announcements/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}"


# Assessment
class Assessment(models.Model):
    ASSESSMENT_TYPE_CHOICES = [
        ('QUIZ', 'Quiz'),
        ('EXAM', 'Exam'),
        ('PROJECT', 'Project'),
        ('RECITATION', 'Recitation'),
        ('ASSIGNMENT', 'Assignment'),
    ]
    
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage weight in final grade")
    date_given = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['date_given']

    def __str__(self):
        return f"{self.course_offering.course.course_code} - {self.title}"


# Assessment Score
class AssessmentScore(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='scores')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='assessment_scores')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)
    date_recorded = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assessment', 'enrollment')

    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.assessment.title} - {self.score}"




# Student Document Request
class DocumentRequest(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('TOR', 'Transcript of Records'),
        ('CERT_GRADES', 'Certificate of Grades'),
        ('CERT_ENROLLMENT', 'Certificate of Enrollment'),
        ('GOOD_MORAL', 'Certificate of Good Moral'),
        ('DIPLOMA', 'Diploma'),
        ('CAV', 'Certificate of Authentication and Verification'),
    ]
    
    REQUEST_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('READY', 'Ready for Pickup'),
        ('CLAIMED', 'Claimed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='document_requests')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    purpose = models.TextField()
    copies = models.PositiveIntegerField(default=1)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='PENDING')
    claimed_date = models.DateTimeField(null=True, blank=True)
    processing_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.student.student_id} - {self.get_document_type_display()}"


# Event
class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('ACADEMIC', 'Academic'),
        ('SEMINAR', 'Seminar'),
        ('WORKSHOP', 'Workshop'),
        ('SPORTS', 'Sports'),
        ('CULTURAL', 'Cultural'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    venue = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_events')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    banner_image = models.ImageField(upload_to='events/', blank=True, null=True)

    class Meta:
        ordering = ['-start_datetime']

    def __str__(self):
        return self.title


# Event Registration
class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'student')
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.student.student_id} - {self.event.title}"


# Notification
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('ANNOUNCEMENT', 'Announcement'),
        ('GRADE', 'Grade Posted'),
        ('ASSIGNMENT', 'Assignment'),
        ('EVENT', 'Event'),
        ('PAYMENT', 'Payment'),
        ('GENERAL', 'General'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True)  # Link to related content

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


# Feedback/Suggestion
class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('COMPLAINT', 'Complaint'),
        ('SUGGESTION', 'Suggestion'),
        ('INQUIRY', 'Inquiry'),
        ('PRAISE', 'Praise'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('REVIEWED', 'Reviewed'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_responses')
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = "Feedback"

    def __str__(self):
        return f"{self.student.student_id} - {self.subject}"


# Course Evaluation
class CourseEvaluation(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='evaluation')
    teaching_effectiveness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    course_content = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    learning_resources = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    assessment_fairness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    overall_satisfaction = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.enrollment.student.student_id} - {self.enrollment.course_offering.course.course_code}"