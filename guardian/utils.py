"""
django-guardian helper functions/classes.
"""
import logging
from django.contrib.auth.models import User, AnonymousUser, Group
from guardian.exceptions import NotUserNorGroup
from guardian.conf.settings import ANONYMOUS_USER_ID
from itertools import chain

logger = logging.getLogger(__name__)


def get_anonymous_user():
    """
    Returns ``User`` instance (not ``AnonymousUser``) depending on
    ``ANONYMOUS_USER_ID`` configuration.
    """
    return User.objects.get(id=ANONYMOUS_USER_ID)

def get_identity(identity):
    """
    Returns (user_obj, None) or (None, group_obj) tuple depending on what is
    given. Also accepts AnonymousUser instance but would return ``User``
    instead - it is convenient and needed for authorization backend to support
    anonymous users.

    If cannot return proper identity instance ``NotUserNorGroup`` is raised.

    Examples::

       >>> user = User.objects.create(username='joe')
       >>> get_identity(user)
       (<User: joe>, None)

       >>> group = Group.objects.create(name='users')
       >>> get_identity(group)
       (None, <Group: users>)

       >>> anon = AnonymousUser()
       >>> get_identity(anon)
       (<User: AnonymousUser>, None)

       >>> get_identity("not instance")
       ...
       NotUserNorGroup: User/AnonymousUser or Group instance is required (got )

    """
    if isinstance(identity, AnonymousUser):
        identity = get_anonymous_user()

    if isinstance(identity, User):
        return identity, None
    elif isinstance(identity, Group):
        return None, identity

    raise NotUserNorGroup("User/AnonymousUser or Group instance is required "
        "(got %s)" % identity)

def clean_orphan_obj_perms():
    """
    Seeks and removes all object permissions entries pointing at non-existing
    targets.

    Returns number of removed objects.
    """
    from guardian.models import UserObjectPermission
    from guardian.models import GroupObjectPermission


    deleted = 0
    # TODO: optimise
    for perm in chain(UserObjectPermission.objects.all(),
        GroupObjectPermission.objects.all()):
        if perm.content_object is None:
            logger.debug("Removing %s (pk=%d)" % (perm, perm.pk))
            perm.delete()
            deleted += 1
    logger.info("Total removed orphan object permissions instances: %d" %
        deleted)
    return deleted

