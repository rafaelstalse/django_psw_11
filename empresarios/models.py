from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from datetime import date

class Empresas(models.Model):
    tempo_existencia_choices = (
        ('-6', 'Menos de 6 meses'),
        ('+6', 'Mais de 6 meses'),
        ('+1', 'Mais de 1 ano'),
        ('+5', 'Mais de 5 anos')
        
    )
    estagio_choices = (
        ('I', 'Tenho apenas uma idea'),
        ('MVP', 'Possuo um MVP'),
        ('MVPP', 'Possuo um MVP com clientes pagantes'),
        ('E', 'Empresa pronta para escalar'),
    )
    area_choices = (
        ('ED', 'Ed-tech'),
        ('FT', 'Fintech'),
        ('AT', 'Agrotech'),
        
    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=30)
    site = models.URLField()
    tempo_existencia = models.CharField(max_length=2, choices=tempo_existencia_choices, default='-6')
    descricao = models.TextField() 
    data_final_captacao = models.DateField()
    percentual_equity = models.IntegerField() # Percentual esperado
    estagio = models.CharField(max_length=4, choices=estagio_choices, default='I')
    area = models.CharField(max_length=3, choices=area_choices)
    publico_alvo = models.CharField(max_length=3)
    valor = models.DecimalField(max_digits=9, decimal_places=2) # Valor total a ser vendido
    pitch = models.FileField(upload_to='pitchs')
    logo = models.FileField(upload_to='logo')

    def __str__(self):
        return f'{self.user.username} | {self.nome}'
    
    @property
    def status(self):
        if date.today() > self.data_final_captacao:
            return mark_safe('<span class="badge bg-success">Captação finalizada</span>')
        return mark_safe('<span class="badge bg-primary">Em captação</span>')
    
    
    @property
    def valuation(self):
        return float(f'{(100 * self.valor) / self.percentual_equity:.2f}')
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
    

class Documento(models.Model):
    empresa = models.ForeignKey(Empresas, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    arquivo = models.FileField(upload_to="documentos")

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
    
    
class Metricas(models.Model):
    empresa = models.ForeignKey(Empresas, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    valor = models.FloatField()

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = 'Metrica'
        verbose_name_plural = 'Metricas'