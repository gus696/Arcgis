import arcpy
import sys

# Configurações de ambiente
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r''


# Criação de duas classes de exceção personalizadas para tratamento de erros
# Serão usadas posteriormente para tratar casos específicos de erro
class nascEmpty(Exception):
    pass


class rioEmpty(Exception):
    pass


# Configuração de inputs e outputs
gdb = r''
nasc = arcpy.GetParameterAsText(0)
hidr = arcpy.GetParameterAsText(2)
nascB = r'in_memory\NascentesBuffer'
hidrB = r'in_memory\HidroBuffer'
appMerge = r'in_memory\AppMerge'
appFinal = arcpy.GetParameterAsText(4)
distN = arcpy.GetParameterAsText(1)
distH = arcpy.GetParameterAsText(3)

# Início do bloco try-except
try:
    nCount = arcpy.GetCount_management(nasc)
    if int(nCount[0]) > 0:
        arcpy.AddMessage('Iniciando o processamento da APP de nascentes')
        # Execução dos buffers
        nasAPP = arcpy.Buffer_analysis(nasc, nascB, f'{distN} Meters')
        # print('Buffer de nascentes executado')
        arcpy.AddMessage('APP de nascentes finalizado...')
    else:
        # Exceção raise: se a camada de nascentes não tiver dados, exceções personalizadas são levantadas abaixo
        raise nascEmpty

    hCount = arcpy.GetCount_management(hidr)
    if int(hCount[0]) > 0:
        arcpy.AddMessage('Iniciando o processamento da APP de hidrografia')
        hidAPP = arcpy.Buffer_analysis(hidr, hidrB, f'{distH} Meters')
        arcpy.AddMessage('APP de hidrografia finalizado')
        # print('Buffer de hidrografia executado')
    else:
        # Exceção raise: se a camada de hidrografia não tiver dados, exceções personalizadas são levantadas abaixo
        raise rioEmpty

    # Junção das camadas
    arcpy.AddMessage('Juntando áreas de APP de nascentes e hidrografia')
    appm = arcpy.Merge_management(inputs=[nasAPP, hidAPP], output=appMerge)
    # print('Merge executado')
    arcpy.AddMessage('Junção finalizada')

    # Dissolve dos limites
    arcpy.AddMessage('Última etapa: agregando polígonos...')
    appd = arcpy.Dissolve_management(appm, appFinal)
    # print('Dissolve executado \nScript finalizado!')
    arcpy.AddMessage('Dissolve executado \nScript finalizado!')

# Exceções levantadas anteriormente e mensagem de erro personalizada
except nascEmpty:
    arcpy.AddError('Erro: A camada de nascentes não possui geometrias')

except rioEmpty:
    arcpy.AddError('Erro: A camada de hidrografia não possui geometrias')

# Demais erros python
except Exception:
    e = sys.exc_info()[1]
    arcpy.AddError(e.args[0])

# Adicionar o resultado ao mapa
aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.activeMap
m.addDataFromPath(appFinal)
del aprx
