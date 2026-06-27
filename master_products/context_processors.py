from master_products.models import ChatMessage


def unread_chat_count(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'unread_count': 0}

    user = request.user
    unread_messages = ChatMessage.objects.filter(is_read=False)

    if getattr(user, 'role', None) == 'customer':
        unread_messages = unread_messages.filter(room__customer=user).exclude(sender=user)
    elif getattr(user, 'role', None) == 'brand':
        unread_messages = unread_messages.filter(room__brand__user_id=user).exclude(sender=user)
    else:
        unread_messages = unread_messages.none()

    return {'unread_count': unread_messages.count()}
