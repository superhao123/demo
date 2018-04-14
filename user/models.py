from django.db import models


class User(models.Model):
    SEX = (
        ('M', '男'),
        ('F', '女'),
        ('U', '保密'),
    )

    nickname = models.CharField(max_length=32, unique=True)  # 昵称
    password = models.CharField(max_length=128)              # 密码
    icon = models.ImageField()                               # 头像
    age = models.IntegerField()                              # 年龄
    sex = models.CharField(choices=SEX, max_length=8)        # 性别

    def has_permission(self, perm_name):
        '''检查用户是否具备某个权限'''
        perm_id = Permission.objects.get(name=perm_name).id  # 取出相应权限的 id
        return UserPermRelation.objects.filter(uid=self.id, perm_id=perm_id).exists()


class Permission(models.Model):
    '''
    create   发帖权限
    edit     修改权限
    comment  评论权限
    delpost  删帖权限
    delcmt   删评论权限
    deluser  删用户权限
    '''
    name = models.CharField(max_length=32)


class UserPermRelation(models.Model):
    uid = models.IntegerField()
    perm_id = models.IntegerField()

    @classmethod
    def add_permission(cls, uid, perm_name):
        '''给用户添加权限'''
        perm = Permission.objects.get(name=perm_name)
        cls.objects.get_or_create(uid=uid, perm_id=perm.id)

    @classmethod
    def del_permission(cls, uid, perm_name):
        '''删除用户权限'''
        perm = Permission.objects.get(name=perm_name)
        try:
            relation = cls.objects.get(uid=uid, perm_id=perm.id)
        except UserPermRelation.DoesNotExist:
            return
        relation.delete()
