from .models import User


def have_conditions_to_register_user(body):
    conditions = True
    errors = {}
    try:
        User.objects.get(cpf_cnpj=body['cpf_cnpj'])
        errors['cpf_cnpj'] = 'CPF ou CNPJ já usado em outro cadastro.'
        conditions = False
    except Exception:
        pass

    try:
        User.objects.get(email=body['email'])
        errors['email'] = 'Email já usado em outro cadastro.'
        conditions = False
    except Exception:
        pass

    try:
        User.objects.get(username=body['username'])
        errors['username'] = 'Username já usado em outro cadastro.'
        conditions = False
    except Exception:
        pass

    try:
        User.objects.get(phone=body['phone'])
        errors['phone'] = 'Numero de telefone já usado em outro cadastro.'
        conditions = False
    except Exception:
        pass

    try:
        User.objects.get(whatsapp=body['whatsapp'])
        errors['whatsapp'] = 'Numero de whatsapp já usado em outro cadastro.'
        conditions = False
    except Exception:
        pass

    return conditions, errors
