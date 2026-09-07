from django import forms

from .models import Comment, Post
from .moderation import is_toxic


MODERATION_ERROR = (
    'Комментарий не проходит модерацию. '
    'Пожалуйста, сформулируйте мысль корректнее'
)


class PostForm(forms.ModelForm):
    """Форма создания и редактирования публикации."""

    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'category', 'location', 'image']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 10, 'cols': 40}),
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
