from django.contrib import admin
from .models import (
    Tag, Designer, DesignCase, ProcessStep,
    ProjectSection, DesignImage, Review,
    SavedDesign, SiteStat, DesignSubmission, SiteImage,
    WhySection, CTABanner,
    MarketplaceStat, TrendingChallenge          # ← add these two
)


@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ('get_key_display', 'image', 'updated_at')
    list_display_links = ('get_key_display',)
    readonly_fields = ('updated_at',)

    fieldsets = (
        (None, {
            'fields': ('key', 'image', 'alt_text'),
            'description': (
                '<strong>Keys and their sections:</strong><br>'
                '<code>hero</code> → Hero section illustration<br>'
                '<code>why_improve</code> → "Improve Your Skills" (image 79)<br>'
                '<code>why_solve</code> → "Solve Real Problems" (image 80)<br>'
                '<code>why_hired</code> → "Get Hired" (image 81)<br>'
                '<code>cta_left</code> → CTA Banner left (image 83)<br>'
                '<code>cta_right</code> → CTA Banner right (image 84)<br>'
            ),
        }),
        ('Meta', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Designer)
class DesignerAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'rating', 'projects_count', 'location', 'years_experience')
    list_editable = ('projects_count',)
    search_fields = ('name', 'role')
    list_filter = ('role',)


class ProcessStepInline(admin.TabularInline):
    model = ProcessStep
    extra = 1
    ordering = ('order',)


class ProjectSectionInline(admin.TabularInline):
    model = ProjectSection
    extra = 1


class DesignImageInline(admin.TabularInline):
    model = DesignImage
    extra = 1


@admin.register(DesignCase)
class DesignCaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'designer', 'status', 'difficulty', 'is_featured', 'is_trending', 'is_challenge', 'order', 'company_name')
    list_editable = ('order', 'is_featured', 'is_trending', 'is_challenge', 'status', 'difficulty')
    list_filter = ('status', 'difficulty', 'is_featured', 'is_trending', 'is_challenge')
    search_fields = ('title', 'designer__name', 'company_name')
    filter_horizontal = ('tags',)
    ordering = ('order', '-created_at')
    inlines = [ProcessStepInline, ProjectSectionInline, DesignImageInline]

    fieldsets = (
        ('Basic Info', {
            'fields': ('order', 'title', 'description', 'image', 'designer', 'tags'),
        }),
        ('Display Flags', {
            'fields': ('is_featured', 'is_trending', 'is_challenge'),
        }),
        ('Marketplace', {
            'fields': ('status', 'difficulty', 'prize', 'problem_statement',
                       'solution_summary', 'engagement_label', 'progress_pct'),
        }),
        # 👇 ADD THIS NEW FIELDSET
        ('Problem Detail Page (appears on /problem/<id>)', {
            'fields': ('company_name', 'company_description', 'deadline', 'platform',
                       'requirements', 'submission_guidelines'),
            'description': 'These fields are shown on the problem detail page (right sidebar and main content).',
        }),
        ('Stats', {
            'fields': ('likes', 'applicants', 'days_left', 'preview_image'),
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'design', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user_name', 'design__title')


@admin.register(SiteStat)
class SiteStatAdmin(admin.ModelAdmin):
    list_display = ('order', 'number', 'label')
    ordering = ('order',)


@admin.register(DesignSubmission)
class DesignSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'overall_score', 'submitted_at')
    list_filter = ('overall_score',)
    search_fields = ('user__username', 'problem__title')
    readonly_fields = ('submitted_at', 'updated_at')


@admin.register(WhySection)
class WhySectionAdmin(admin.ModelAdmin):
    list_display = ('step', 'title', 'point1', 'point2')
    ordering = ('step',)


@admin.register(CTABanner)
class CTABannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'designers', 'companies', 'button_text')


# ── MARKETPLACE STAT ────────────────────────────────────────
@admin.register(MarketplaceStat)
class MarketplaceStatAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'number', 'color')
    list_editable = ('order', 'title', 'number', 'color')
    list_display_links = None


# ── TRENDING CHALLENGE ──────────────────────────────────────
@admin.register(TrendingChallenge)
class TrendingChallengeAdmin(admin.ModelAdmin):
    list_display = ('order', 'badge_type', 'title', 'company', 'reward', 'designers_count', 'closing_text', 'closing_color', 'case')
    list_editable = ('order', 'badge_type', 'title', 'company', 'reward', 'designers_count', 'closing_text', 'closing_color', 'case')   
    list_display_links = None
    list_filter = ('badge_type', 'closing_color')
    search_fields = ('title', 'company')
    fieldsets = (
        ('Basic Info', {
            'fields': ('order', 'badge_type', 'title', 'company', 'reward', 'designers_count')
        }),
        ('Link to Design Case (for "Solve Now")', {
            'fields': ('case', 'link')     # ← add this line
        }),
        ('Closing Info', {
            'fields': ('closing_text', 'closing_color')
        }),
        ('Image', {
            'fields': ('image',)
        }),
    )