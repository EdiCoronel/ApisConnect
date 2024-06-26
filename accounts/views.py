from django.shortcuts import get_object_or_404

# Create your views here.

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import ListUserSerializer, UserSerializer, RegisterSerializer, CitasSerializer
from django.contrib.auth import login

from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView

from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser   

# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


# Api Citas

from .models import Citas
from rest_framework import viewsets 

# Create your views here.

class CitasViewSet(viewsets.ModelViewSet):
    queryset = Citas.objects.all()
    serializer_class = CitasSerializer

# Lista de Usuarios

from rest_framework.views import APIView

class ListUser(APIView):
    def get(self, request, pk=None):
        if pk is not None:
            user = get_object_or_404(User, pk=pk)
            serializer = ListUserSerializer(user)
            return Response(serializer.data)
        else:
            users = User.objects.all()
            serializer = ListUserSerializer(users, many=True)
            return Response(serializer.data)
    
    def post(self, request):
        serializer = ListUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = ListUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    
    def delete(self, request, pk):
        user = User.objects.get(pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Perfil de Usuario

from rest_framework import generics, permissions
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

class UserDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.request.user.pk)
    

@api_view(['GET'])
def api_root(request, format=None):
    # Intenta obtener el primer objeto Citas, si existe
    try:
        primera_cita = Citas.objects.first()
        pk_cita = primera_cita.pk if primera_cita else None
    except Citas.DoesNotExist:
        pk_cita = None
    
    # Intenta obtener el pk del primer usuario
    try:
        primer_usuario = User.objects.first()
        user_pk = primer_usuario.pk if primer_usuario else None
    except User.DoesNotExist:
        user_pk = None

    # Genera la respuesta con los enlaces de la API
    response_dict = {
        'register': reverse('register', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'logout': reverse('logout', request=request, format=format),
        'citas': reverse('citas', request=request, format=format),
        'user-list': reverse('user-list', request=request, format=format),
        'user-detail': reverse('user-detail', request=request, format=format),
    }

    # Solo agrega el enlace para citas-detalle si existe un pk de cita
    if pk_cita:
        response_dict['citas-detalle'] = reverse('citas-detalle', kwargs={'pk': pk_cita}, request=request, format=format)

    # Solo agrega el enlace para user-detail-list si existe un pk de usuario
    if user_pk:
        response_dict['user-detail-list'] = reverse('user-detail-list', kwargs={'pk': user_pk}, request=request, format=format)

    return Response(response_dict)