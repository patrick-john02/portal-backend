from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AcademicYear, Semester, Department, Faculty, Student, Program,
    Course, CourseOffering, Schedule, Enrollment, Grade,
    Announcement, Assessment, AssessmentScore, DocumentRequest,
    Event, EventRegistration, Notification, Feedback, CourseEvaluation
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('-start_date',)
    list_editable = ('is_active',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_type', 'academic_year', 'start_date', 'end_date', 'is_active', 'enrollment_period')
    list_filter = ('is_active', 'semester_type', 'academic_year')
    search_fields = ('semester_type', 'academic_year__name')
    ordering = ('-start_date',)
    list_editable = ('is_active',)
    date_hierarchy = 'start_date'
    
    def enrollment_period(self, obj):
        return f"{obj.enrollment_start} to {obj.enrollment_end}"
    enrollment_period.short_description = 'Enrollment Period'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'head', 'email', 'phone', 'building')
    list_filter = ('building',)
    search_fields = ('name', 'code', 'email')
    ordering = ('name',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Management', {
            'fields': ('head',)
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'building')
        }),
    )


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'title', 'department', 'employment_status', 'is_active')
    list_filter = ('employment_status', 'is_active', 'department', 'title')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('user__last_name',)
    list_editable = ('is_active',)
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Employment Information', {
            'fields': ('employee_id', 'department', 'title', 'employment_status', 'date_hired', 'is_active')
        }),
        ('Professional Details', {
            'fields': ('specialization', 'bio')
        }),
        ('Contact & Office', {
            'fields': ('contact_number', 'office_room', 'consultation_hours')
        }),
    )
    
    def full_name(self, obj):
        return obj.user.get_full_name()
    full_name.short_description = 'Name'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'department', 'year_level', 'status', 'enrolled_at')
    list_filter = ('status', 'year_level', 'department', 'enrolled_at')
    search_fields = ('student_id', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('student_id',)
    date_hierarchy = 'enrolled_at'
    list_editable = ('status',)
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'student_id')
        }),
        ('Academic Information', {
            'fields': ('department', 'year_level', 'status', 'enrolled_at')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'address', 'contact_number', 'profile_picture')
        }),
        ('Emergency Contacts', {
            'fields': ('emergency_contact_name', 'emergency_contact_number', 'guardian_name', 'guardian_contact')
        }),
    )
    
    def full_name(self, obj):
        return obj.user.get_full_name()
    full_name.short_description = 'Name'


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'degree_type', 'department', 'total_units', 'duration_years')
    list_filter = ('degree_type', 'department')
    search_fields = ('name', 'code')
    ordering = ('code',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'department', 'units', 'course_type', 'year_level', 'semester_offered')
    list_filter = ('course_type', 'department', 'year_level', 'semester_offered')
    search_fields = ('course_code', 'title')
    ordering = ('course_code',)
    filter_horizontal = ('prerequisites',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course_code', 'title', 'description', 'department')
        }),
        ('Course Details', {
            'fields': ('units', 'lecture_hours', 'lab_hours', 'course_type')
        }),
        ('Academic Planning', {
            'fields': ('year_level', 'semester_offered', 'prerequisites')
        }),
    )


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1
    fields = ('day_of_week', 'start_time', 'end_time', 'room', 'building')


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'section', 'semester', 'faculty', 'enrolled_count', 'max_slots', 'available_slots_display', 'is_active')
    list_filter = ('semester', 'course__department', 'is_active')
    search_fields = ('course__course_code', 'course__title', 'section', 'faculty__user__last_name')
    ordering = ('course', 'section')
    list_editable = ('is_active',)
    inlines = [ScheduleInline]
    
    fieldsets = (
        ('Course Information', {
            'fields': ('course', 'semester', 'section')
        }),
        ('Assignment', {
            'fields': ('faculty',)
        }),
        ('Capacity', {
            'fields': ('max_slots', 'enrolled_count', 'is_active')
        }),
    )
    
    def available_slots_display(self, obj):
        available = obj.available_slots
        color = 'green' if available > 10 else 'orange' if available > 0 else 'red'
        return format_html('<span style="color: {};">{}</span>', color, available)
    available_slots_display.short_description = 'Available Slots'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course_offering', 'day_of_week', 'start_time', 'end_time', 'room', 'building')
    list_filter = ('day_of_week', 'course_offering__semester')
    search_fields = ('course_offering__course__course_code', 'room', 'building')
    ordering = ('day_of_week', 'start_time')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_offering', 'date_enrolled', 'status', 'dropped_date')
    list_filter = ('status', 'date_enrolled', 'course_offering__semester')
    search_fields = ('student__student_id', 'student__user__first_name', 'student__user__last_name', 'course_offering__course__course_code')
    ordering = ('-date_enrolled',)
    date_hierarchy = 'date_enrolled'
    list_editable = ('status',)
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'course_offering', 'date_enrolled', 'status')
        }),
        ('Additional Information', {
            'fields': ('dropped_date',)
        }),
    )


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student_display', 'course_display', 'midterm_grade', 'final_grade', 'final_rating', 'remarks', 'date_submitted')
    list_filter = ('final_rating', 'remarks', 'enrollment__course_offering__semester')
    search_fields = ('enrollment__student__student_id', 'enrollment__student__user__first_name', 'enrollment__student__user__last_name', 'enrollment__course_offering__course__course_code')
    ordering = ('-date_submitted',)
    date_hierarchy = 'date_submitted'
    
    def student_display(self, obj):
        return obj.enrollment.student.student_id
    student_display.short_description = 'Student ID'
    
    def course_display(self, obj):
        return obj.enrollment.course_offering.course.course_code
    course_display.short_description = 'Course'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'posted_by', 'priority', 'target_audience', 'is_active', 'created_at', 'expiry_date')
    list_filter = ('priority', 'target_audience', 'is_active', 'department', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_editable = ('is_active', 'priority')
    
    fieldsets = (
        ('Announcement Details', {
            'fields': ('title', 'content', 'attachment')
        }),
        ('Targeting', {
            'fields': ('department', 'target_audience', 'priority')
        }),
        ('Publishing', {
            'fields': ('posted_by', 'is_public', 'is_active', 'expiry_date')
        }),
    )


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_offering', 'assessment_type', 'max_score', 'weight', 'date_given')
    list_filter = ('assessment_type', 'date_given', 'course_offering__semester')
    search_fields = ('title', 'course_offering__course__course_code')
    ordering = ('-date_given',)
    date_hierarchy = 'date_given'


@admin.register(AssessmentScore)
class AssessmentScoreAdmin(admin.ModelAdmin):
    list_display = ('student_display', 'assessment', 'score', 'percentage', 'date_recorded')
    list_filter = ('assessment__assessment_type', 'date_recorded')
    search_fields = ('enrollment__student__student_id', 'assessment__title')
    ordering = ('-date_recorded',)
    date_hierarchy = 'date_recorded'
    
    def student_display(self, obj):
        return obj.enrollment.student.student_id
    student_display.short_description = 'Student ID'
    
    def percentage(self, obj):
        if obj.assessment.max_score > 0:
            pct = (obj.score / obj.assessment.max_score) * 100
            color = 'green' if pct >= 75 else 'orange' if pct >= 60 else 'red'
            return format_html('<span style="color: {};">{:.2f}%</span>', color, pct)
        return '-'
    percentage.short_description = 'Percentage'


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'document_type', 'copies', 'status', 'request_date', 'processing_fee', 'claimed_date')
    list_filter = ('document_type', 'status', 'request_date')
    search_fields = ('student__student_id', 'student__user__first_name', 'student__user__last_name')
    ordering = ('-request_date',)
    date_hierarchy = 'request_date'
    list_editable = ('status',)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('student', 'document_type', 'purpose', 'copies')
        }),
        ('Status', {
            'fields': ('status', 'processing_fee', 'remarks')
        }),
        ('Dates', {
            'fields': ('request_date', 'claimed_date')
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_datetime', 'end_datetime', 'venue', 'organizer', 'max_participants', 'is_published')
    list_filter = ('event_type', 'is_published', 'department', 'start_datetime')
    search_fields = ('title', 'venue', 'organizer__username')
    ordering = ('-start_datetime',)
    date_hierarchy = 'start_datetime'
    list_editable = ('is_published',)
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'event_type', 'banner_image')
        }),
        ('Schedule', {
            'fields': ('start_datetime', 'end_datetime', 'venue')
        }),
        ('Organization', {
            'fields': ('organizer', 'department', 'max_participants')
        }),
        ('Publishing', {
            'fields': ('is_published',)
        }),
    )


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'event', 'registration_date', 'attended', 'certificate_issued')
    list_filter = ('attended', 'certificate_issued', 'registration_date', 'event__event_type')
    search_fields = ('student__student_id', 'student__user__first_name', 'student__user__last_name', 'event__title')
    ordering = ('-registration_date',)
    date_hierarchy = 'registration_date'
    list_editable = ('attended', 'certificate_issued')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_editable = ('is_read',)
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('recipient', 'notification_type', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'link')
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'feedback_type', 'subject', 'status', 'submitted_at', 'responded_by', 'responded_at')
    list_filter = ('feedback_type', 'status', 'submitted_at')
    search_fields = ('student__student_id', 'subject', 'message')
    ordering = ('-submitted_at',)
    date_hierarchy = 'submitted_at'
    list_editable = ('status',)
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('student', 'feedback_type', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Response', {
            'fields': ('response', 'responded_by', 'responded_at')
        }),
    )


@admin.register(CourseEvaluation)
class CourseEvaluationAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'teaching_effectiveness', 'course_content', 'learning_resources', 'assessment_fairness', 'overall_satisfaction', 'submitted_at', 'is_anonymous')
    list_filter = ('is_anonymous', 'submitted_at', 'overall_satisfaction')
    search_fields = ('enrollment__student__student_id', 'enrollment__course_offering__course__course_code', 'comments')
    ordering = ('-submitted_at',)
    date_hierarchy = 'submitted_at'
    readonly_fields = ('submitted_at',)
    
    fieldsets = (
        ('Evaluation Information', {
            'fields': ('enrollment', 'is_anonymous')
        }),
        ('Ratings', {
            'fields': ('teaching_effectiveness', 'course_content', 'learning_resources', 'assessment_fairness', 'overall_satisfaction')
        }),
        ('Comments', {
            'fields': ('comments', 'submitted_at')
        }),
    )