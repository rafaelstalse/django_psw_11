from django.shortcuts import render, redirect
from .models import Empresas
from django.contrib import messages
from django.contrib.messages import constants
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import re


def cadastrar_empresa(request):
    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa estar logado para cadastrar empresas')
        return redirect('/usuarios/logar')
    
    if request.method == "GET":
        return render(request, 'cadastrar_empresa.html', {'tempo_existencia': Empresas.tempo_existencia_choices, 'areas': Empresas.area_choices })
    
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final = request.POST.get('data_final')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.get('estagio')
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')
        
        # add validações
        if not nome:
            messages.add_message(request, constants.ERROR, 'O nome é obrigatório.')
            return redirect('/empresarios/cadastrar_empresa')

        if not cnpj or not re.match(r'\d{14}', cnpj):
            messages.add_message(request, constants.ERROR, 'CNPJ inválido.')
            return redirect('/empresarios/cadastrar_empresa')

        url_validator = URLValidator()
        try:
            url_validator(site)
        except ValidationError:
            messages.add_message(request, constants.ERROR, 'URL do site inválida.')
            return redirect('/empresarios/cadastrar_empresa')
        
        if data_final:
            try:
                data_final = datetime.strptime(data_final, '%Y-%m-%d')
                data_minima = datetime.now() + timedelta(days=3)
                if data_final < data_minima:
                    messages.add_message(request, constants.ERROR, 'A data final deve ser pelo menos 3 dias após hoje.')
                    return redirect('/empresarios/cadastrar_empresa')
            except ValueError:
                messages.add_message(request, constants.ERROR, 'Data final inválida.')
                return redirect('/empresarios/cadastrar_empresa')

        try:
            percentual_equity = float(percentual_equity)
            if percentual_equity < 5 or percentual_equity > 90:
                raise ValueError
        except ValueError:
            messages.add_message(request, constants.ERROR, 'Percentual de equity deve ser um número entre 5 e 90.')
            return redirect('/empresarios/cadastrar_empresa')

        try:
            valor = float(valor)
            if valor < 0:
                raise ValueError
        except ValueError:
            messages.add_message(request, constants.ERROR, 'O valor deve ser um número positivo.')
            return redirect('/empresarios/cadastrar_empresa')

        if not area:
            messages.add_message(request, constants.ERROR, 'A área é obrigatória.')
            return redirect('/empresarios/cadastrar_empresa')

        if not estagio:
            messages.add_message(request, constants.ERROR, 'O estágio é obrigatório.')
            return redirect('/empresarios/cadastrar_empresa')
        
        try:
            empresa = Empresas(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo
            )
            empresa.save()
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do servidor')
            return redirect('/empresarios/cadastrar_empresa')
        
        messages.add_message(request, constants.SUCCESS, 'Empresa criada com sucesso')
        return redirect('/empresarios/cadastrar_empresa')
    
    
def listar_empresas(request):
    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa estar logado para listar empresas')
        return redirect('/usuarios/logar')
    
    if request.method == "GET":
        # realizar os filtros das empresas
        empresas = Empresas.objects.filter(user=request.user)
        return render(request, 'listar_empresas.html', {'empresas': empresas})
    

def empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    if request.method == "GET":
        return render(request, 'empresa.html', {'empresa': empresa})