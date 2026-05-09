from django.db import models
from django.contrib.auth.models import User


# ── TAG ──────────────────────────────────────────────────────
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ── DESIGNER ─────────────────────────────────────────────────
class Designer(models.Model):
    name              = models.CharField(max_length=100)
    bio               = models.TextField(blank=True)
    profile_image     = models.ImageField(upload_to='designers/', blank=True, null=True)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='designer',
        null=True,      # temporarily allow null for existing designers that don't yet have a user
        blank=True
    )
    role              = models.CharField(max_length=100, default='UI/UX Designer')
    rating            = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    projects_count = models.PositiveIntegerField(default=0, help_text="Manual project count (overrides automatic count from DesignCase)")
    location          = models.CharField(max_length=100, blank=True, default='San Francisco, CA')
    years_experience  = models.PositiveIntegerField(default=0)
    education         = models.TextField(blank=True, help_text="Degree, university, year")
    experience        = models.TextField(blank=True, help_text="Previous jobs (one per line)")
    achievements      = models.TextField(blank=True, help_text="Awards, certifications")
    # Add these fields to Designer model
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills, e.g. 'UI/UX, Figma, Web App'")
    achievements = models.TextField(blank=True, help_text="One achievement per line, e.g. 'Top Designer Award\nCompleted 25 Challenges'")
    availability = models.CharField(max_length=100, blank=True, default="Available for Hire, Quick Response, Open for Freelance/Full Time")
    # For stats bar:
    problems_saved = models.CharField(max_length=20, blank=True, default="48K+")
    worked_companies = models.CharField(max_length=20, blank=True, default="15+")
    # Success rate (already has rating, but add explicit success_pct)
    success_rate = models.PositiveIntegerField(default=99, help_text="Percentage, e.g. 99")
    featured_case     = models.ForeignKey(
        'DesignCase',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='featured_for_designer',
        help_text="Select one of your design cases to feature on your profile"
    )

    def __str__(self):
        return self.name

    @property
    def project_count(self):
        return self.designcase_set.count()

    @property
    def experience_list(self):
        lines = self.experience.strip().split('\n') if self.experience else []
        items = []
        for line in lines:
            if ' – ' in line:
                parts = line.split(' – ')
                title_company = parts[0]
                period = parts[1] if len(parts) > 1 else ''
                if ' at ' in title_company:
                    title, company = title_company.split(' at ', 1)
                else:
                    title, company = title_company, ''
                items.append({'title': title.strip(), 'company': company.strip(), 'period': period.strip()})
            else:
                items.append({'title': line.strip(), 'company': '', 'period': ''})
        return items

    class Meta:
        ordering = ['-rating']


# ── DESIGN CASE ───────────────────────────────────────────────
class DesignCase(models.Model):
    STATUS_CHOICES = [
        ('open',     'Open'),
        ('progress', 'In Progress'),
        ('done',     'Completed'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy',   'Easy'),
        ('medium', 'Medium'),
        ('hard',   'Hard'),
    ]

    order             = models.PositiveIntegerField(default=0)
    title             = models.CharField(max_length=200)
    description       = models.TextField()
    image             = models.ImageField(upload_to='cases/', blank=True, null=True)

    designer          = models.ForeignKey(Designer, on_delete=models.CASCADE)
    tags              = models.ManyToManyField(Tag, blank=True)

    is_featured       = models.BooleanField(default=False)
    is_trending       = models.BooleanField(default=False)
    is_challenge      = models.BooleanField(default=False)

    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    difficulty        = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy')
    prize             = models.CharField(max_length=20, blank=True)
    problem_statement = models.TextField(blank=True)
    solution_summary  = models.TextField(blank=True)
    engagement_label  = models.CharField(max_length=60, blank=True)
    progress_pct      = models.PositiveIntegerField(default=0)
    # Problem detail page content
    company_name = models.CharField(max_length=100, blank=True, default="Netbank")
    company_description = models.TextField(blank=True, default="Netbank is a leading digital banking platform focused on delivering modern, secure, and user-friendly financial services.")
    deadline = models.CharField(max_length=50, blank=True, default="April 30, 2026")
    platform = models.CharField(max_length=100, blank=True, default="Mobile+Web")

    # Requirements – user can enter one bullet point per line
    requirements = models.TextField(blank=True, help_text="Enter each requirement on a new line. They will be displayed as bullet points.")
    
    # Submission Guidelines – one per line
    submission_guidelines = models.TextField(blank=True, help_text="Enter each guideline on a new line. They will be displayed as bullet points.")
    likes             = models.PositiveIntegerField(default=0)
    applicants        = models.PositiveIntegerField(default=0)
    days_left         = models.CharField(max_length=40, blank=True)
    preview_image = models.ImageField(upload_to='cases/previews/', blank=True, null=True,
    help_text="Final Design Preview image (shown in the Overview tab)")
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def designer_name(self):
        return self.designer.name

    class Meta:
        ordering = ['order', '-created_at']


# ── PROCESS STEPS ────────────────────────────────────────────
class ProcessStep(models.Model):
    design      = models.ForeignKey(DesignCase, on_delete=models.CASCADE, related_name='steps')
    title       = models.CharField(max_length=100)
    description = models.TextField()
    order       = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.design.title} — {self.title}"

    class Meta:
        ordering = ['order']


# ── PROJECT SECTIONS ─────────────────────────────────────────
class ProjectSection(models.Model):
    design  = models.ForeignKey(DesignCase, on_delete=models.CASCADE, related_name='sections')
    title   = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return f"{self.design.title} — {self.title}"


# ── DESIGN IMAGES (gallery) ──────────────────────────────────
class DesignImage(models.Model):
    design = models.ForeignKey(DesignCase, on_delete=models.CASCADE, related_name='gallery')
    image  = models.ImageField(upload_to='designs/')

    def __str__(self):
        return self.design.title


# ── REVIEWS ──────────────────────────────────────────────────
class Review(models.Model):
    design     = models.ForeignKey(DesignCase, on_delete=models.CASCADE, related_name='reviews')
    user_name  = models.CharField(max_length=100)
    comment    = models.TextField()
    rating     = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} — {self.design.title}"


# ── SAVED / BOOKMARKS ────────────────────────────────────────
class SavedDesign(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    design   = models.ForeignKey(DesignCase, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'design')

    def __str__(self):
        return f"{self.user.username} saved {self.design.title}"


# ── SITE STATS ───────────────────────────────────────────────
class SiteStat(models.Model):
    order  = models.PositiveIntegerField(default=0)
    number = models.CharField(max_length=20)
    label  = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.number} {self.label}"

    class Meta:
        ordering = ['order']


# ── DESIGN SUBMISSION ────────────────────────────────────────
class DesignSubmission(models.Model):
    VERSION_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    problem       = models.ForeignKey(DesignCase, on_delete=models.CASCADE, related_name='submissions')
    user          = models.ForeignKey(User, on_delete=models.CASCADE)
    figma_link    = models.URLField(blank=True, help_text="Link to Figma design")
    design_images = models.ImageField(upload_to='submissions/', blank=True, null=True)
    description   = models.TextField(blank=True, help_text="Explain your design decisions")

    submitted_at  = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    feedback_data  = models.JSONField(default=dict, blank=True)
    overall_score  = models.PositiveIntegerField(default=0)

    version = models.PositiveIntegerField(default=1)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_versions')
    status = models.CharField(max_length=20, choices=VERSION_STATUS_CHOICES, default='draft')
    improvements_made = models.JSONField(default=list, blank=True)
    change_summary = models.TextField(blank=True)
    impact_preview = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ('problem', 'user', 'version')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} v{self.version}"


# ── SITE IMAGE ───────────────────────────────────────────────
# Used to manage homepage section images from Django admin.
# Each record has a unique `key` that the view looks up.
#
#  Keys used in home view:
#   'hero'            → Hero section illustration
#   'why_improve'     → "Improve Your Skills" illustration  (image 79)
#   'why_solve'       → "Solve Real Problems" illustration  (image 80)
#   'why_hired'       → "Get Hired" illustration            (image 81)
#   'cta_left'        → CTA banner left image               (image 83)
#   'cta_right'       → CTA banner right image              (image 84)

class SiteImage(models.Model):
    KEY_CHOICES = [
        ('hero',        'Hero Section Image'),
        ('why_improve', 'Why – Improve Your Skills (image 79)'),
        ('why_solve',   'Why – Solve Real Problems (image 80)'),
        ('why_hired',   'Why – Get Hired (image 81)'),
        ('cta_left',    'CTA Banner – Left Image (image 83)'),
        ('cta_right',   'CTA Banner – Right Image (image 84)'),
    ]

    key   = models.CharField(
        max_length=30,
        choices=KEY_CHOICES,
        unique=True,
        help_text="Which section this image belongs to"
    )
    image = models.ImageField(
        upload_to='site_images/',
        help_text="Upload the image file"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alt text for accessibility (optional)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_key_display()

    class Meta:
        ordering = ['key']
        verbose_name = 'Site Image'
        verbose_name_plural = 'Site Images'


# ── WHY SECTION ──────────────────────────────────────────────
class WhySection(models.Model):
    step   = models.PositiveIntegerField(
        help_text="Display order: 1, 2, 3"
    )
    title  = models.CharField(max_length=100)
    point1 = models.CharField(max_length=200)
    point2 = models.CharField(max_length=200)
    image  = models.ImageField(
        upload_to='why/',
        blank=True, null=True,
        help_text="Illustration shown below the bullet points"
    )

    def __str__(self):
        return f"Step {self.step}: {self.title}"

    class Meta:
        ordering = ['step']
        verbose_name        = 'Why Section Card'
        verbose_name_plural = 'Why Section Cards'


# ── CTA BANNER ───────────────────────────────────────────────
class CTABanner(models.Model):
    title       = models.CharField(max_length=200)
    subtitle    = models.TextField()
    button_text = models.CharField(max_length=100, default='Hire Designer')
    designers   = models.CharField(
        max_length=20,
        default='1+',
        help_text='e.g. 12,000+'
    )
    companies   = models.CharField(
        max_length=20,
        default='850+',
        help_text='e.g. 850+'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name        = 'CTA Banner'
        verbose_name_plural = 'CTA Banner'

# ── MARKETPLACE STAT (optional, required if you use marketplace_stats in view) ──
class MarketplaceStat(models.Model):
    COLOR_CHOICES = [
        ('green', 'green'),
        ('purple', 'purple'),
        ('blue', 'blue'),
    ]
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='purple')
    title = models.CharField(max_length=100)
    number = models.CharField(max_length=30)
    footer = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# ── TRENDING CHALLENGE ───────────────────────────────────────
class TrendingChallenge(models.Model):
    BADGE_CHOICES = [
        ('hot', '🔥 HOT'),
        ('rising', '📈 Rising'),
    ]
    CLOSING_COLOR_CHOICES = [
        ('red', 'red'),
        ('blue', 'blue'),
    ]
    order = models.PositiveIntegerField(default=0)
    badge_type = models.CharField(max_length=10, choices=BADGE_CHOICES, default='hot')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    reward = models.CharField(max_length=50)
    designers_count = models.PositiveIntegerField(default=0)
    closing_text = models.CharField(max_length=100)
    closing_color = models.CharField(max_length=10, choices=CLOSING_COLOR_CHOICES, default='red')
    link = models.URLField(blank=True, help_text="Optional custom URL, else defaults to problem detail")
    image = models.ImageField(upload_to='trending/', blank=True, null=True, help_text="Upload an image for this trending challenge")
    case = models.ForeignKey('DesignCase', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title