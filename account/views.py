from django.views.generic.edit import FormView
from .forms import RegisterForm
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages



class RegisterView(FormView):

    template_name = 'account/register.html'
    form_class = RegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('main')
    
    def get_context_data(self, **kwargs):

        kwargs['title'] = 'Регистрация'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):

        user = form.save()
        if user:
            login(self.request, user)

        return super(RegisterView, self).form_valid(form)
    
class LoginUserView(LoginView):

    template_name = 'account/login.html'
    redirect_authenticated_user = False
    success_url = reverse_lazy('main')
    
    def get_context_data(self, **kwargs):

        kwargs['title'] = 'Авторизация'
        return super().get_context_data(**kwargs)

    def form_invalid(self, form):
        messages.error(self.request,'Неверный логин или пароль')
        return self.render_to_response(self.get_context_data(form=form))
    