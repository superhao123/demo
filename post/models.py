from django.db import models

from user.models import User


class Post(models.Model):
    uid = models.IntegerField()  # 作者的 uid

    title = models.CharField(max_length=64)
    create = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    @property
    def auth(self):
        if not hasattr(self, '_auth'):
            self._auth = User.objects.get(id=self.uid)
        return self._auth

    def comments(self):
        '''当前文章的所有评论'''
        return Comment.objects.filter(pid=self.id).order_by('-create')

    def tags(self):
        pt_relations = PostTagRelation.objects.filter(pid=self.id).only('tid')  # 取出当前 post 所有与 tag 的关系
        tid_list = [pt.tid for pt in pt_relations]  # 获取相关联的 tag id
        return Tag.objects.filter(id__in=tid_list)  # 返回当前 post 的 tags

    def update_tags(self, tag_names):
        tag_names = set(tag_names)

        # 取出当前已具有的 tag names
        curr_tags = self.tags()
        curr_names = set(t.name for t in curr_tags)  # 当前 post 的所有 tag name

        # 增加 Tag
        new_tag_names = tag_names - curr_names
        PostTagRelation.add_relations(self.id, new_tag_names)

        # 删除 tag
        del_tag_names = curr_names - tag_names
        PostTagRelation.del_relations(self.id, del_tag_names)


class Comment(models.Model):
    pid = models.IntegerField()
    uid = models.IntegerField()
    create = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    @property
    def auth(self):
        if not hasattr(self, '_auth'):
            self._auth = User.objects.get(id=self.uid)
        return self._auth

    @property
    def post(self):
        if not hasattr(self, '_post'):
            self._post = Post.objects.get(id=self.pid)
        return self._post


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def posts(self):
        pt_relations = PostTagRelation.objects.filter(tid=self.id).only('pid')  # 取出当前 tag 所有与 post 的关系
        pid_list = [pt.pid for pt in pt_relations]   # 获取相关联的 post id
        return Post.objects.filter(id__in=pid_list)  # 返回当前 tag 的 posts

    @classmethod
    def ensure_tag_names(cls, names):
        '''确保tag存在，如果不存在则创建'''

        # 获取未创建的 tag names
        old_tags = cls.objects.filter(name__in=names)  # 已存在的 tag
        old_names = set(t.name for t in old_tags)      # 已存在的 tag_name
        new_names = set(names) - old_names  # 需要新创建的 tag_name

        # 创建 new tags
        need_create = [cls(name=name) for name in new_names]  # 待创建的 tags 空对象 (当前未与数据库发生交互)
        cls.objects.bulk_create(need_create)

        return cls.objects.filter(name__in=names)


class PostTagRelation(models.Model):
    '''
    pid     tid
    ===     ======
      1     9 (Python)
      1     8 (Django)
      1     4 (Linux)
      3     9 (Python)
      7     9 (Python)
     11     4 (Linux)
    '''
    pid = models.IntegerField()
    tid = models.IntegerField()

    @classmethod
    def add_relations(cls, pid, tag_names):
        '''添加新的关系'''
        tags = Tag.ensure_tag_names(tag_names)  # 确保传入的 Tag 存在，并取出

        # new_relations = []
        # for t in tags:
        #     relation = cls(pid=pid, tid=t.id)
        #     new_relations.append(relation)
        new_relations = [cls(pid=pid, tid=t.id) for t in tags]  # 生成待创建关系对象
        PostTagRelation.objects.bulk_create(new_relations)

    @classmethod
    def del_relations(cls, pid, tag_names):
        '''删除关系'''
        tags = Tag.objects.filter(name__in=tag_names).only('id')
        tid_list = [t.id for t in tags]
        cls.objects.filter(pid=pid, tid__in=tid_list).delete()
