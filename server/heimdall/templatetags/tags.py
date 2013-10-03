from django import template
from django.template import resolve_variable, NodeList
from django.contrib.auth.models import Group, User

from heimdall.models import UserRoles, Roles

register = template.Library()

@register.tag()
def ifusergroup(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup Admins %} ... {% endifusergroup %}, or
           {% ifusergroup Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.split_contents()
        groups = []
        groups += tokensp[1:]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifusergroup' requires at least 1 argument.")
    
    nodelist_true = parser.parse(('else', 'endifusergroup'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifusergroup',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return GroupCheckNode(groups, nodelist_true, nodelist_false)

class GroupCheckNode(template.Node):
    def __init__(self, groups, nodelist_true, nodelist_false):
        self.groups = groups
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable('user', context)
        
        if not user.is_authenticated():
            return self.nodelist_false.render(context)
        
        allowed = False
        for checkgroup in self.groups:
            try:
                group = Group.objects.get(name=checkgroup)
            except Group.DoesNotExist:
                break
                
        if group in user.groups.all():
            allowed = True
        
        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
            
            




@register.tag()
def ifisa(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup User Admins %} ... {% endifusergroup %}, or
           {% ifusergroup User Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.contents.split()
        user = tokensp[1]
        groups = []
        groups += tokensp[2:]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifisa' requires at least 2 arguments.")
    
    nodelist_true = parser.parse(('else', 'endifisa'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifisa',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return GroupCheck(user, groups, nodelist_true, nodelist_false)




@register.tag()
def ifhasroletype(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifhasroletype Admins %} ... {% ifhasroletype %}, or
           {% ifhasroletype Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.contents.split()
        user = tokensp[1]
        roletype = []
        roletype += tokensp[2:]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifhasroletype' requires at least 2 arguments.")
    
    nodelist_true = parser.parse(('else', 'endifhasroletype'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifhasroletype',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return RoleTypeCheck(user, roletype, nodelist_true, nodelist_false)



class RoleTypeCheck(template.Node):
    def __init__(self, oneusername, groups, nodelist_true, nodelist_false):
        self.groups = groups
        self.oneusername = oneusername
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        allowed = False
        
        user = resolve_variable('user', context)
        userroles = UserRoles.objects.filter(user=user)

        for role in userroles:
            if role.role.type == 'MANAGER':
                allowed = True
                break
        
        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
            



@register.tag()
def ifhasrole(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifhasroletype Admins %} ... {% ifhasroletype %}, or
           {% ifhasroletype Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokensp = token.contents.split()
        user = tokensp[1]
        roletype = tokensp[2]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifhasrole' requires at least 2 arguments.")
    
    nodelist_true = parser.parse(('else', 'endifhasrole'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifhasrole',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return RoleCheck(user, roletype, nodelist_true, nodelist_false)


class RoleCheck(template.Node):
    def __init__(self, oneusername, role, nodelist_true, nodelist_false):
        self.role = role
        self.oneusername = oneusername
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable(self.oneusername, context)
        role = resolve_variable(self.role, context)
        
        role = Roles.objects.get(name=role);
        if UserRoles.objects.filter(user=user, role = role):
            print "false"
            return self.nodelist_true.render(context)
        else:
            print "true"
            return self.nodelist_false.render(context)


class GroupCheck(template.Node):
    def __init__(self, oneusername, groups, nodelist_true, nodelist_false):
        self.groups = groups
        self.oneusername = oneusername
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable(self.oneusername, context)
        
        allowed = False
        for checkgroup in self.groups:
            try:
                group = Group.objects.get(name=checkgroup)
            except Group.DoesNotExist:
                try:
                    checkgroup = resolve_variable(checkgroup, context)
                    group = Group.objects.get(name=checkgroup)
                except Group.DoesNotExist:
                    break
                break
                
            
        if group in user.groups.all():
            allowed = True
        
        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
            

