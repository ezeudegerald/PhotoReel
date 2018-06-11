from .imports import *


class PhotoSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    description = serializers.CharField(style={'base_template': 'textarea.html'})
    location = serializers.CharField(initial='unknown')
    image = serializers.ImageField(required=True)
    user = serializers.ReadOnlyField(source='user.username')

    def create(self, validated_data):
        validated_data.user = self.user
        return Photo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


class PhotoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'title', 'description', 'location', 'image', 'user', 'created_on')

        title = serializers.CharField(required=False)
        description = serializers.CharField(style={'base_template': 'textarea.html'})
        location = serializers.CharField(initial='unknown')
        image = serializers.ImageField(required=True)


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoModelSerializer
