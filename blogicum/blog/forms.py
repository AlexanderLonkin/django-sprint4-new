from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post
from .moderation import is_toxic

User = get_user_model()


MODERATION_ERROR = (
    'Комментарий не проходит модерацию. '
    'Пожалуйста, сформулируйте мысль корректнее'
)


class PostForm(forms.ModelForm):
    """Форма создания и редактирования публикации."""

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'category',
            'location',
            'image',
            'is_published',
        )
        widgets = {
            'text': forms.Textarea(attrs={'rows': 10, 'cols': 40}),
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
        }


class CommentForm(forms.ModelForm):
    """Форма комментария с проверкой текста на токсичность."""

    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        """Проверить текст комментария и вернуть безопасное значение."""
        text = self.cleaned_data['text']
        if is_toxic(text):
            raise forms.ValidationError(MODERATION_ERROR)
        return text


class UserEditForm(forms.ModelForm):
    """Форма редактирования общедоступных данных пользователя."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Придумайте уникальное имя',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ваш email для связи',
            }),
        }
