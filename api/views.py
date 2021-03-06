from django.http import JsonResponse
from django.db.models import Count
from datetime import datetime, timedelta
from home.models import *


def historic(request, period, type, id):
    now = datetime.now().date()

    if period == 'week':
        interval = 1
        amount = 7
        mask = '%d/%m'

    elif period == 'month':
        interval = 1
        amount = 30
        mask = '%d/%m'

    elif period == 'year':
        interval = 30
        amount = 12
        mask = '%b'
        now = now.replace(day=1)


    days = [now - timedelta(days=x * interval) for x in range(amount)]
    days.reverse()

    problems_solved = []
    for day in days:
        if type == 'group':
            problems_solved.append(Solution.objects.filter(date__range=[day, day + timedelta(days=interval)]).count())
        elif type == 'team':
            problems_solved.append(Solution.objects.filter(
                date__range=[day, day + timedelta(days=interval)],
                profile__in=Team.objects.get(pk=id).profiles.all()).count())
        elif type == 'profile':
            problems_solved.append(Solution.objects.filter(
                date__range=[day, day + timedelta(days=interval)],
                profile__id=id).count())

    days = [d.strftime(mask) for d in days]

    return JsonResponse({
        'xAxis': days,
        'series': problems_solved
    })


def confirm_secret_key(request):
    if request.method == 'POST':
        secret_key = request.POST['secret_key']
        group_id = request.POST['group_id']
        success = False

        group = Group.objects.filter(id=group_id, secret_key_user=secret_key).first()

        if group:
            success = True
            request.user.profile.role = 'user'
            request.user.profile.group = group
            request.user.profile.save()

        group = Group.objects.filter(id=group_id, secret_key_coach=secret_key).first()

        if group:
            success = True
            request.user.profile.role = 'coach'
            request.user.profile.group = group
            request.user.profile.save()

        group = Group.objects.filter(id=group_id, secret_key_visitor=secret_key).first()

        if group:
            success = True
            request.user.profile.role = 'visitor'
            request.user.profile.group = group
            request.user.profile.save()


        return JsonResponse({
            'success': success
        })


def histogram(request, type, type_id, year, month, category):    
    if type == 'group':
        profiles = Profile.objects.filter(group_id=type_id)
    elif type == 'team':
        profiles = Profile.objects.get(id=type_id).profiles
    elif type == 'profile':
        profiles = [Profile.objects.get(id=type_id)]

    # todo fix this
    profiles = Profile.objects.all()

    filters = {
        'profile__in': profiles,
        'date__month': month,
        'date__year': year,
    }

    if category != 'all':
        filters['problem__category'] = category

    results = Solution.objects.values('problem__level')\
                    .annotate(count=Count('problem__level'))\
                    .filter(**filters)\
                    .order_by('problem__level')

    series = [0] * 10

    for result in results:
        series[result['problem__level']] = result['count']

    return JsonResponse({
        'series': series
    })