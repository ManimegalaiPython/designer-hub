from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count
from django.db.models import Case, When, Value, IntegerField
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings


from .models import DesignCase, SiteStat, Tag, Designer, SiteImage, WhySection, CTABanner


# ── Helper: fetch a SiteImage URL by key ─────────────────────
def _site_img(key):
    obj = SiteImage.objects.filter(key=key).first()
    return obj.image.url if obj else None


# ── HOME ─────────────────────────────────────────────────────
def home(request):
    desired_open_title = 'Redesign Onboarding Flow for a Fintech App'
    open_cases = DesignCase.objects.filter(status='open').annotate(
        custom_order=Case(
            When(title=desired_open_title, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('custom_order', 'order', '-created_at')[:1]

    progress_cases = DesignCase.objects.filter(status='progress').order_by('order', '-created_at')[:1]
    done_cases     = DesignCase.objects.filter(status='done').order_by('order', '-created_at')[:1]

    cases    = DesignCase.objects.select_related('designer').prefetch_related('tags').order_by('order', '-created_at')
    stats    = SiteStat.objects.all()
    why_data = WhySection.objects.all()
    cta      = CTABanner.objects.first()

    return render(request, 'hubapp/home.html', {
        'cases': cases,
        'stats': stats,
        'open_cases': open_cases,
        'progress_cases': progress_cases,
        'done_cases': done_cases,
        'why_data': why_data,
        'cta': cta,
        'hero_image':      _site_img('hero'),
        'why_img_improve': _site_img('why_improve'),
        'why_img_solve':   _site_img('why_solve'),
        'why_img_hired':   _site_img('why_hired'),
        'cta_img_left':    _site_img('cta_left'),
        'cta_img_right':   _site_img('cta_right'),
    })


# ── EXPLORE ──────────────────────────────────────────────────
from django.db.models import Q, Count, Case, When, Value, IntegerField

def explore(request):
    query        = request.GET.get('q', '').strip()
    selected_tag = request.GET.get('tag', '')

    base_qs = DesignCase.objects.select_related('designer').prefetch_related('tags')

    if query:
        base_qs = base_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(designer__name__icontains=query)
        )

    if selected_tag and selected_tag.isdigit():
        base_qs = base_qs.filter(tags__id=selected_tag)

    featured_cases  = base_qs.filter(is_featured=True)[:3]
    trending_cases  = base_qs.order_by('-likes')[:3]
    challenge_cases = base_qs.filter(is_challenge=True)[:3]

    desired_names = ['Emma Williams', 'Rahul Sinha', 'Olivia Clarke']
    top_designers = Designer.objects.filter(name__in=desired_names).annotate(
        total_projects=Count('designcase')
    ).order_by('-total_projects', '-rating')[:3]

    if top_designers.count() < 3:
        extra = Designer.objects.exclude(name__in=desired_names).annotate(
            total_projects=Count('designcase')
        ).filter(total_projects__gt=0).order_by('-total_projects', '-rating')[:3 - top_designers.count()]
        top_designers = list(top_designers) + list(extra)

    desired_open_title = 'Redesign Onboarding Flow for a Fintech App'
    open_cases = DesignCase.objects.filter(status='open').annotate(
        custom_order=Case(
            When(title=desired_open_title, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('custom_order', 'order', '-created_at')[:1]

    progress_cases = DesignCase.objects.filter(status='progress').order_by('order', '-created_at')[:1]
    done_cases     = DesignCase.objects.filter(status='done').order_by('order', '-created_at')[:1]

    ALLOWED_TAGS  = ['All', 'UI/UX', 'Mobile', 'Web', 'Branding', 'Motion', '3D']
    filtered_tags = Tag.objects.filter(name__in=ALLOWED_TAGS[1:]).order_by('name')
    tag_order     = {name: i for i, name in enumerate(ALLOWED_TAGS[1:])}
    filtered_tags = sorted(filtered_tags, key=lambda t: tag_order.get(t.name, 99))

    return render(request, 'hubapp/explore.html', {
        'all_tags':        filtered_tags,
        'query':           query,
        'selected_tag':    selected_tag,
        'cases':           base_qs,
        'featured_cases':  featured_cases,
        'trending_cases':  trending_cases,
        'challenge_cases': challenge_cases,
        'top_designers':   top_designers,
        'open_cases':      open_cases,
        'progress_cases':  progress_cases,
        'done_cases':      done_cases,
    })


# ── MARKETPLACE ──────────────────────────────────────────────
from django.db.models import Count, F, Case, When, Value, IntegerField
from .models import TrendingChallenge, MarketplaceStat

def marketplace(request):
    status_filter     = request.GET.get('status', 'all')
    difficulty_filter = request.GET.get('difficulty', '')

    all_cases = DesignCase.objects.select_related('designer').prefetch_related('tags')
    if difficulty_filter:
        all_cases = all_cases.filter(difficulty=difficulty_filter)

    desired_open_title = 'Redesign Onboarding Flow for a Fintech App'
    open_cases = all_cases.filter(status='open').annotate(
        custom_order=Case(
            When(title=desired_open_title, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('custom_order', 'order', '-created_at')[:1]

    progress_cases = all_cases.filter(status='progress').order_by('order', '-created_at')[:1]
    done_cases     = all_cases.filter(status='done').order_by('order', '-created_at')[:1]

    trending_challenges = TrendingChallenge.objects.all().order_by('order')
    marketplace_stats   = MarketplaceStat.objects.all().order_by('order')

    top_designers = Designer.objects.annotate(
        total_projects=F('projects_count')
    ).annotate(
        custom_order=Case(
            When(name__iexact='Priya Nair',   then=Value(0)),
            When(name__iexact='Arjun Raj',    then=Value(1)),
            When(name__iexact='Sneha Iyer',   then=Value(2)),
            default=Value(10),
            output_field=IntegerField()
        )
    ).order_by('custom_order', '-total_projects', '-rating')[:3]

    return render(request, 'hubapp/marketplace.html', {
        'open_cases':          open_cases,
        'progress_cases':      progress_cases,
        'done_cases':          done_cases,
        'status':              status_filter,
        'difficulty':          difficulty_filter,
        'trending_challenges': trending_challenges,
        'marketplace_stats':   marketplace_stats,
        'top_designers':       top_designers,
    })


# ── SIGNUP ───────────────────────────────────────────────────
from .models import Designer   # <-- make sure this import is present

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name  = request.POST.get("last_name")
        email      = request.POST.get("email")
        password   = request.POST.get("password")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists")
            return redirect("signup")

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )

        # ✅ Create a Designer profile linked to this user
        Designer.objects.create(
            user=user,
            name=f"{first_name} {last_name}".strip(),
            # other fields will use their default values (role, rating, etc.)
        )

        messages.success(request, "Account created. Please login.")
        return redirect("login")

    return render(request, "hubapp/signup.html")


# ── LOGIN ─────────────────────────────────────────────────────
def login_view(request):
    if request.method == "POST":
        email    = request.POST.get("email")
        password = request.POST.get("password")
        user     = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "hubapp/login.html")


# ── LOGOUT ───────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect("login")


# ── UPLOAD ───────────────────────────────────────────────────
def upload(request):
    return render(request, 'hubapp/upload.html')


# ── DESIGNER PROFILE ─────────────────────────────────────────
# ── DESIGNER PROFILE ─────────────────────────────────────────
def designer_profile(request, designer_id):
    designer = get_object_or_404(Designer, id=designer_id)

    # ----- MASTER DEFAULT CONTENT (same as Sneha Iyer) -----
    default_bio = (
        "I am a passionate UI/UX designer with a strong focus on creating intuitive "
        "and visually engaging digital experiences. I enjoy solving real-world problems "
        "through user-centered design and thoughtful interaction patterns. With experience "
        "in mobile and web design, I specialize in crafting clean interfaces, improving "
        "usability, and delivering impactful design solutions."
    )
    default_education = "B.A in Graphic & Interactive Design – University of California, Berkeley (2018)"
    default_skills = "UI/UX, Figma, Web App, Mobile Design, Adobe XD, Prototyping, User Experience"
    default_experience = [
        {"title": "Senior UI/UX Designer", "company": "XYZ Company", "period": "2022 - Present"},
        {"title": "Product Designer", "company": "ABC Studio", "period": "2019 - 2022"},
    ]

    # Only set fields that are writable (CharField, TextField)
    if not designer.bio:
        designer.bio = default_bio
    if not designer.education:
        designer.education = default_education
    if not designer.skills:
        designer.skills = default_skills

    # DO NOT assign to designer.experience_list (it’s not writable)
    # Instead, we will pass default_experience to template.

    # Featured case fallback
    if not designer.featured_case:
        designer.featured_case = DesignCase.objects.filter(is_featured=True).first()

    # Portfolio cases fallback
    portfolio_cases = designer.designcase_set.prefetch_related('tags').all()
    
    if not portfolio_cases.exists():
        # Hardcoded default portfolio by title order
        default_titles = [
            "Colorful Branding",
            "Redesign a Fitness App",
            "Habit Flow App",          # or merge with above?
            "Grocery App UI",
            "ONLINE PHARMACY",
            "Cosmetic Website",
            "Online Pharmacy Website",
        ]
        # Fetch existing cases that match these titles (order preserved)
        portfolio_cases = list(DesignCase.objects.filter(title__in=default_titles))
        # Optionally sort them to match default_titles order
        title_order = {title: i for i, title in enumerate(default_titles)}
        portfolio_cases.sort(key=lambda case: title_order.get(case.title, 999))

    return render(request, 'hubapp/designer_profile.html', {
        'designer': designer,
        'portfolio_cases': portfolio_cases,
    })

# ── CASE DETAIL ──────────────────────────────────────────────
def case_detail(request, pk):
    case = get_object_or_404(
        DesignCase.objects
        .select_related('designer')
        .prefetch_related('tags', 'steps', 'sections', 'gallery', 'reviews'),
        pk=pk
    )
    more_projects = (
        DesignCase.objects
        .filter(designer=case.designer)
        .exclude(pk=pk)
        .prefetch_related('tags')
        .order_by('order', '-created_at')[:5]
    )
    return render(request, 'hubapp/case_detail.html', {
        'case':          case,
        'more_projects': more_projects,
    })


# ── PROBLEM DETAIL ───────────────────────────────────────────
def problem_detail(request, pk):
    problem = get_object_or_404(
        DesignCase.objects.select_related('designer').prefetch_related('tags'),
        pk=pk
    )
    return render(request, 'hubapp/problem_detail.html', {'problem': problem})


# ── SUBMIT SOLUTION ──────────────────────────────────────────
def submit_solution(request, pk):
    problem = get_object_or_404(DesignCase, pk=pk)
    if request.method == "POST":
        return render(request, 'hubapp/submission_success_screen.html', {'problem': problem})
    return render(request, 'hubapp/submit_solution_page.html', {'problem': problem})


# ── AI DESIGN FEEDBACK ───────────────────────────────────────
def ai_design_feedback(request, pk):
    problem = get_object_or_404(DesignCase, pk=pk)
    return render(request, 'hubapp/ai_design_feedback_report.html', {'problem': problem})


# ── REFINE SOLUTION ──────────────────────────────────────────
def refine_solution(request, pk):
    problem = get_object_or_404(DesignCase, pk=pk)
    return render(request, 'hubapp/refined_solution_download.html', {'problem': problem})


# ── UPDATE SUBMISSION ────────────────────────────────────────
def update_submission(request, pk):
    problem = get_object_or_404(DesignCase, pk=pk)
    return render(request, 'hubapp/update_submission.html', {'problem': problem})


# ── SUBMISSION UPDATED SUCCESS ───────────────────────────────
def submission_updated_success(request, pk):
    problem = get_object_or_404(DesignCase, pk=pk)
    return render(request, 'hubapp/submission_updated_success.html', {'problem': problem})




from openai import OpenAI
from django.conf import settings

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)
@csrf_exempt
@require_http_methods(["POST"])
def proxy_gemini(request):
    try:
        data = json.loads(request.body)

        user_content = ""

        for msg in data.get("messages", []):
            if msg.get("role") == "user":
                user_content = str(msg.get("content", ""))
                break

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            temperature=0.5,
            max_tokens=300
        )

        generated_text = completion.choices[0].message.content

        return JsonResponse({
            "content": [
                {
                    "text": generated_text
                }
            ]
        })

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)