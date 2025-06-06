def nav_context(request):
    context = {}
    if request.user.is_authenticated:
        try:
            context['pending_incidents'] = request.user.reported_incidents.filter(status='OPEN').count()
        except AttributeError:
            context['pending_incidents'] = 0
    return context