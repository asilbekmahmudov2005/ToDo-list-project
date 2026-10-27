import json
import calendar
from datetime import datetime, timedelta, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.utils import timezone
from .models import Task
from .forms import TaskForm, RegisterForm


def get_greeting():
    """Vaqtga mos salomlashuv matni"""
    current_hour = timezone.localtime().hour
    if 5 <= current_hour < 11:
        return "Xayrli tong"
    elif 11 <= current_hour < 17:
        return "Xayrli kun"
    elif 17 <= current_hour < 22:
        return "Xayrli kech"
    else:
        return "Xayrli tun"


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Ro‘yxatdan muvaffaqiyatli o‘tdingiz! Tizimga kiring.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'planner/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {user.first_name or user.username}!")
                return redirect('dashboard')
        else:
            messages.error(request, "Foydalanuvchi nomi yoki parol noto‘g‘ri kiritildi.")
    else:
        form = AuthenticationForm()
    return render(request, 'planner/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('login')


@login_required
def dashboard_view(request):
    today = timezone.localdate()
    greeting = get_greeting()
    
    user_tasks = Task.objects.filter(user=request.user)
    today_tasks = user_tasks.filter(date=today)
    
    total_today = today_tasks.count()
    completed_today = today_tasks.filter(is_completed=True).count()
    pending_today = total_today - completed_today
    progress_percentage = int((completed_today / total_today * 100)) if total_today > 0 else 0

    task_form = TaskForm(initial={'date': today})

    context = {
        'greeting': greeting,
        'today': today,
        'today_tasks': today_tasks,
        'total_today': total_today,
        'completed_today': completed_today,
        'pending_today': pending_today,
        'progress_percentage': progress_percentage,
        'task_form': task_form,
        'active_menu': 'dashboard',
    }
    return render(request, 'planner/dashboard.html', context)


@login_required
def today_tasks_view(request):
    today = timezone.localdate()
    tasks = Task.objects.filter(user=request.user, date=today)
    
    # Qidiruv va filterlar
    query = request.GET.get('q')
    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
    category = request.GET.get('category')
    if category:
        tasks = tasks.filter(category=category)
        
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)
        
    status = request.GET.get('status')
    if status == 'completed':
        tasks = tasks.filter(is_completed=True)
    elif status == 'pending':
        tasks = tasks.filter(is_completed=False)

    sort = request.GET.get('sort', 'time')
    if sort == 'time':
        tasks = tasks.order_by('start_time', '-created_at')
    elif sort == 'priority':
        tasks = tasks.order_by('-priority', 'start_time')
    elif sort == 'title':
        tasks = tasks.order_by('title')

    task_form = TaskForm(initial={'date': today})

    context = {
        'tasks': tasks,
        'today': today,
        'task_form': task_form,
        'active_menu': 'today',
        'categories': Task.Category.choices,
        'priorities': Task.Priority.choices,
    }
    return render(request, 'planner/today_tasks.html', context)


@login_required
def all_tasks_view(request):
    tasks = Task.objects.filter(user=request.user)

    # Qidiruv va filter
    query = request.GET.get('q')
    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))

    date_filter = request.GET.get('date')
    if date_filter:
        tasks = tasks.filter(date=date_filter)

    category = request.GET.get('category')
    if category:
        tasks = tasks.filter(category=category)

    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)

    status = request.GET.get('status')
    if status == 'completed':
        tasks = tasks.filter(is_completed=True)
    elif status == 'pending':
        tasks = tasks.filter(is_completed=False)

    sort = request.GET.get('sort', 'date_desc')
    if sort == 'date_desc':
        tasks = tasks.order_by('-date', 'start_time')
    elif sort == 'date_asc':
        tasks = tasks.order_by('date', 'start_time')
    elif sort == 'priority':
        tasks = tasks.order_by('-priority', '-date')
    elif sort == 'title':
        tasks = tasks.order_by('title')

    task_form = TaskForm(initial={'date': timezone.localdate()})

    context = {
        'tasks': tasks,
        'task_form': task_form,
        'active_menu': 'all_tasks',
        'categories': Task.Category.choices,
        'priorities': Task.Priority.choices,
    }
    return render(request, 'planner/all_tasks.html', context)


@login_required
def calendar_view(request):
    today = timezone.localdate()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    cal = calendar.Calendar(firstweekday=0) # Dushanbadan boshlanadi
    month_days = cal.monthdatescalendar(year, month)

    start_date = month_days[0][0]
    end_date = month_days[-1][-1]

    tasks_in_range = Task.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    )

    tasks_by_date = {}
    for task in tasks_in_range:
        date_str = task.date.strftime('%Y-%m-%d')
        if date_str not in tasks_by_date:
            tasks_by_date[date_str] = []
        tasks_by_date[date_str].append(task)

    month_names_uz = [
        "", "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]

    selected_date_str = request.GET.get('date', today.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today

    selected_date_tasks = Task.objects.filter(user=request.user, date=selected_date)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    task_form = TaskForm(initial={'date': selected_date})

    context = {
        'year': year,
        'month': month,
        'month_name': month_names_uz[month],
        'month_days': month_days,
        'today': today,
        'tasks_by_date': tasks_by_date,
        'selected_date': selected_date,
        'selected_date_tasks': selected_date_tasks,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'task_form': task_form,
        'active_menu': 'calendar',
    }
    return render(request, 'planner/calendar.html', context)


@login_required
def statistics_view(request):
    user_tasks = Task.objects.filter(user=request.user)
    today = timezone.localdate()

    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    overall_percentage = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    # 1. So'nggi 7 kun statistikasi (kunlik)
    last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    daily_labels = [d.strftime('%d.%m') for d in last_7_days]
    daily_completed = []
    daily_total = []

    for d in last_7_days:
        day_tasks = user_tasks.filter(date=d)
        daily_total.append(day_tasks.count())
        daily_completed.append(day_tasks.filter(is_completed=True).count())

    # 2. So'nggi 4 hafta natijalari
    weekly_labels = []
    weekly_completed = []
    weekly_total = []
    for w in range(3, -1, -1):
        w_start = today - timedelta(days=today.weekday() + 7 * w)
        w_end = w_start + timedelta(days=6)
        label = f"{w_start.strftime('%d.%m')} - {w_end.strftime('%d.%m')}"
        weekly_labels.append(label)
        w_tasks = user_tasks.filter(date__range=[w_start, w_end])
        weekly_total.append(w_tasks.count())
        weekly_completed.append(w_tasks.filter(is_completed=True).count())

    # 3. So'nggi 6 oy natijalari
    monthly_labels = []
    monthly_completed = []
    monthly_total = []
    month_names_uz = ["", "Yan", "Fev", "Mar", "Apr", "May", "Iyun", "Iyul", "Avg", "Sen", "Okt", "Noy", "Dek"]
    
    for m_offset in range(5, -1, -1):
        # Calculate month and year
        m_calc = today.month - m_offset
        y_calc = today.year
        while m_calc <= 0:
            m_calc += 12
            y_calc -= 1
        monthly_labels.append(f"{month_names_uz[m_calc]} {y_calc}")
        m_tasks = user_tasks.filter(date__year=y_calc, date__month=m_calc)
        monthly_total.append(m_tasks.count())
        monthly_completed.append(m_tasks.filter(is_completed=True).count())

    # 4. Kategoriya bo'yicha taqsimot
    cat_labels_map = dict(Task.Category.choices)
    category_counts = user_tasks.values('category').annotate(count=Count('id'))
    category_data = {cat_labels_map.get(k, k): 0 for k in dict(Task.Category.choices).keys()}
    for item in category_counts:
        cat_key = item['category']
        label = cat_labels_map.get(cat_key, cat_key)
        category_data[label] = item['count']

    # 5. Muhimlik darajasi bo'yicha taqsimot
    prio_labels_map = dict(Task.Priority.choices)
    priority_counts = user_tasks.values('priority').annotate(count=Count('id'))
    priority_data = {prio_labels_map.get(k, k): 0 for k in dict(Task.Priority.choices).keys()}
    for item in priority_counts:
        p_key = item['priority']
        label = prio_labels_map.get(p_key, p_key)
        priority_data[label] = item['count']

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overall_percentage': overall_percentage,
        'daily_labels': json.dumps(daily_labels),
        'daily_completed': json.dumps(daily_completed),
        'daily_total': json.dumps(daily_total),
        'weekly_labels': json.dumps(weekly_labels),
        'weekly_completed': json.dumps(weekly_completed),
        'weekly_total': json.dumps(weekly_total),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_completed': json.dumps(monthly_completed),
        'monthly_total': json.dumps(monthly_total),
        'category_labels': json.dumps(list(category_data.keys())),
        'category_values': json.dumps(list(category_data.values())),
        'priority_labels': json.dumps(list(priority_data.keys())),
        'priority_values': json.dumps(list(priority_data.values())),
        'active_menu': 'statistics',
    }
    return render(request, 'planner/statistics.html', context)


@login_required
def settings_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip()
        request.user.first_name = first_name
        request.user.email = email
        request.user.save()
        messages.success(request, "Profil maʼlumotlari muvaffaqiyatli saqlandi.")
        return redirect('settings')

    context = {
        'active_menu': 'settings',
    }
    return render(request, 'planner/settings.html', context)


# --- CRUD API & AJAX Endpoints ---

@login_required
@require_POST
def task_create_view(request):
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
        messages.success(request, f"«{task.title}» vazifasi muvaffaqiyatli yaratildi.")
        
        # AJAX so'rovi bo'lsa JSON qaytaramiz
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'is_completed': task.is_completed,
                    'priority': task.get_priority_display(),
                    'category': task.get_category_display(),
                    'date': str(task.date),
                }
            })
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        for field, errs in form.errors.items():
            for err in errs:
                messages.error(request, f"{field}: {err}")
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def task_detail_json(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    return JsonResponse({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'date': task.date.strftime('%Y-%m-%d'),
        'start_time': task.start_time.strftime('%H:%M') if task.start_time else '',
        'end_time': task.end_time.strftime('%H:%M') if task.end_time else '',
        'duration': task.duration or '',
        'priority': task.priority,
        'category': task.category,
        'is_completed': task.is_completed,
    })


@login_required
@require_POST
def task_update_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    form = TaskForm(request.POST, instance=task)
    if form.is_valid():
        form.save()
        messages.success(request, f"«{task.title}» vazifasi muvaffaqiyatli yangilandi.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        for field, errs in form.errors.items():
            for err in errs:
                messages.error(request, f"{field}: {err}")
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
@require_POST
def task_delete_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    title = task.title
    task.delete()
    messages.success(request, f"«{title}» vazifasi o‘chirildi.")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
@require_POST
def task_toggle_status_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.is_completed = not task.is_completed
    task.save()
    status_msg = "bajarildi deb belgilandi" if task.is_completed else "faol holatga qaytarildi"
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Dashboard yoki ro'yxat statistikasi uchun yangi ma'lumotlar
        today = timezone.localdate()
        today_tasks = Task.objects.filter(user=request.user, date=today)
        total_today = today_tasks.count()
        completed_today = today_tasks.filter(is_completed=True).count()
        pending_today = total_today - completed_today
        progress = int((completed_today / total_today * 100)) if total_today > 0 else 0

        return JsonResponse({
            'success': True,
            'is_completed': task.is_completed,
            'total_today': total_today,
            'completed_today': completed_today,
            'pending_today': pending_today,
            'progress_percentage': progress,
            'message': f"«{task.title}» {status_msg}."
        })
    messages.success(request, f"«{task.title}» {status_msg}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
