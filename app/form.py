from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FunkoPop, Category


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class FunkoPopForm(forms.ModelForm, forms.ImageField):
    class Meta:
        model = FunkoPop
        fields = ('collection', 'title', 'price', 'description', 'image', 'rate', 'category')

    def save(self, commit=True):
        funko = super(FunkoPopForm, self).save(commit=False)
        if commit:
            funko.save()
        return funko


class CategoryForm(forms.ModelForm, forms.ImageField):
    class Meta:
        model = Category
        fields = ('title', 'image')

    def save(self, commit=True):
        category = super(CategoryForm, self).save(commit=False)
        if commit:
            category.save()
        return category