from rest_framework import serializers
from django.contrib.auth.models import User
from blog_api.models import Post, Comment, Category, PostImages

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6,write_only=True, required=True)
    password2 = serializers.CharField(min_length=6,write_only=True,required=True)
    first_name = serializers.CharField(required=True)
    last_name =serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')

    def validate_first_name(self, value):
        if not value.istitle():
            raise serializers.ValidationError("Name must start with uppercase")
        return value
    def validate(selfself, attrs):
        password2 = attrs.pop('password2')
        if attrs['password'] != password2 :
            raise serializers.ValidationError("Password did not match !")
        return attrs
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name'),# .get otlichasetsya ot kvadratnoi skopki tem chto on vovrashaet None esli net takogo klyucha
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_active', 'is_staff')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.children.exists():
            representation['children'] = CategorySerializer(instance=instance.children.all(), many=True).data
        return representation

class PostImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostImages
        exclude = ('id',)



class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    comments = serializers.PrimaryKeyRelatedField(many =True, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    #post = serializers.ReadOnlyField(source='post.title')

    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'owner','created_at', 'comments', 'category','preview' , 'images')

    def validate(self, attrs):
        print(attrs)
        return super().validate(attrs)

    def create(self, validated_data):
        print(validated_data)
        request = self.context.get('request')
        images_data = request.FILES
        created_post = Post.objects.create(**validated_data)
        print(created_post)
        print("Work: ", images_data.getlist('images'))
        print("Is not work: ", images_data)
        # for images_data in images_data.getlist('images'):
        #     PostImages.objects.create(post=created_post,image = images_data)
        images_obj = [PostImages(post = created_post, image=image)
                      for image in images_data.getlist('images')]
        PostImages.objects.bulk_create(images_obj)
        return  created_post
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    owner =serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Comment
        fields = ('id', 'body', 'owner', 'post',)





