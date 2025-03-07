from django.shortcuts import render, redirect
from .models import Empresas, Documento, Metricas
from django.contrib import messages
from django.contrib.messages import constants
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from investidores.models import PropostaInvestimento
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
        nome_empresa = request.GET.get('empresa')

        empresas = Empresas.objects.filter(user=request.user)
        if nome_empresa:
            empresas = empresas.filter(nome__icontains=nome_empresa)
        
        return render(request, 'listar_empresas.html', {'empresas': empresas})
    

def empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Você não pode visualizar essa empresa")
        return redirect(f'/empresarios/listar_empresas')
    
    if request.method == "GET":
        documentos = Documento.objects.filter(empresa=empresa)
        proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
        proposta_investimentos_enviada = proposta_investimentos.filter(status='PE')
        
        percentual_vendido = 0
        for pi in proposta_investimentos:
            if pi.status == 'PA':
                percentual_vendido = percentual_vendido + pi.percentual
        
        total_captado = sum(proposta_investimentos.filter(status='PA').values_list('valor', flat=True))         
        valuation_atual = (100 * float(total_captado)) / float(percentual_vendido) if percentual_vendido != 0 else 0
        
        return render(request, 'empresa.html', {'empresa': empresa, 
                                                'documentos': documentos, 
                                                'proposta_investimentos_enviada': proposta_investimentos_enviada, 
                                                'percentual_vendido': int(percentual_vendido),
                                                'total_captado': total_captado,
                                                'valuation_atual': valuation_atual,
                                                })
    
    
def add_doc(request, id):
    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa estar logado para adicionar documentos')
        return redirect('/usuarios/logar')
    
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    extensao = arquivo.name.split('.')
    
    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Você não pode adicionar documentos a essa empresa")
        return redirect(f'/empresarios/listar_empresas')
    
    if extensao[1] != 'pdf':
        messages.add_message(request, constants.ERROR, "Envie apenas PDF's")
        return redirect(f'/empresarios/empresa/{empresa.id}')
    
    if not arquivo:
        messages.add_message(request, constants.ERROR, "Envie um arquivo")
        return redirect(f'/empresarios/empresa/{empresa.id}')
        
    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo
    )
    documento.save()
    
    messages.add_message(request, constants.SUCCESS, "Arquivo cadastrado com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')


def excluir_dc(request, id):
    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa estar logado para remover documentos')
        return redirect('/usuarios/logar')
    
    documento = Documento.objects.get(id=id)
    
    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Esse documento não é seu")
        return redirect(f'/empresarios/empresa/{empresa.id}')
    
    documento.delete()
    messages.add_message(request, constants.SUCCESS, "Documento excluído com sucesso")
    return redirect(f'/empresarios/empresa/{documento.empresa.id}')


def add_metrica(request, id):
    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa estar logado para adicionar métricas')
        return redirect('/usuarios/logar')
    
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    valor = request.POST.get('valor')
    
    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor
    )
    metrica.save()

    messages.add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')


def gerenciar_proposta(request, id):
    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa estar logado para gerenciar propostas')
        return redirect('/usuarios/logar')
    
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)

    if acao == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita')
        pi.status = 'PA'
    elif acao == 'recusar':
        messages.add_message(request, constants.ERROR, 'Proposta recusada')
        pi.status = 'PR'

    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')