"""
Script para testar as validações dos schemas de room booking
"""

import sys
sys.path.append('/home/a5ur4/Documentos/Faculdade/Pocket GO')

from uuid import uuid4
from decimal import Decimal
from database.schemas.room_types_schema import RoomTypesCreate, BillingCycleTypeEnum
from database.schemas.rate_plans_schema import RatePlansCreate
from database.schemas.room_prices_schema import RoomPricesCreate

def test_room_types_validations():
    """Testa validações do RoomTypes"""
    print("🏨 TESTANDO VALIDAÇÕES - ROOM TYPES")
    print("="*50)
    
    hotel_id = uuid4()
    
    # Teste 1: Dados válidos
    try:
        valid_room_type = RoomTypesCreate(
            hotel_id=hotel_id,
            name="Suíte Master",
            description="Quarto luxuoso com vista para o mar",
            capacity=4,
            image_url="https://example.com/suite.jpg"
        )
        print("✅ Dados válidos: OK")
    except Exception as e:
        print(f"❌ Dados válidos: {e}")
    
    # Teste 2: Capacidade zero (deve falhar)
    try:
        invalid_capacity = RoomTypesCreate(
            hotel_id=hotel_id,
            name="Quarto Test",
            capacity=0
        )
        print("❌ Capacidade zero: Deveria ter falhado")
    except Exception as e:
        print("✅ Capacidade zero: Validação funcionando -", str(e))
    
    # Teste 3: Capacidade muito alta (deve falhar)
    try:
        invalid_capacity_high = RoomTypesCreate(
            hotel_id=hotel_id,
            name="Quarto Test",
            capacity=25
        )
        print("❌ Capacidade muito alta: Deveria ter falhado")
    except Exception as e:
        print("✅ Capacidade muito alta: Validação funcionando -", str(e))
    
    # Teste 4: Nome vazio (deve falhar)
    try:
        invalid_name = RoomTypesCreate(
            hotel_id=hotel_id,
            name="   ",
            capacity=2
        )
        print("❌ Nome vazio: Deveria ter falhado")
    except Exception as e:
        print("✅ Nome vazio: Validação funcionando -", str(e))

def test_rate_plans_validations():
    """Testa validações do RatePlans"""
    print("\\n💰 TESTANDO VALIDAÇÕES - RATE PLANS")
    print("="*50)
    
    hotel_id = uuid4()
    
    # Teste 1: Dados válidos
    try:
        valid_rate_plan = RatePlansCreate(
            hotel_id=hotel_id,
            name="Diária Promocional",
            billing_cycle=BillingCycleTypeEnum.NIGHTLY,
            duration_minutes=1440
        )
        print("✅ Dados válidos: OK")
    except Exception as e:
        print(f"❌ Dados válidos: {e}")
    
    # Teste 2: Duração zero (deve falhar)
    try:
        invalid_duration = RatePlansCreate(
            hotel_id=hotel_id,
            name="Plano Test",
            billing_cycle=BillingCycleTypeEnum.HOURLY,
            duration_minutes=0
        )
        print("❌ Duração zero: Deveria ter falhado")
    except Exception as e:
        print("✅ Duração zero: Validação funcionando -", str(e))
    
    # Teste 3: Duração muito alta (deve falhar)
    try:
        invalid_duration_high = RatePlansCreate(
            hotel_id=hotel_id,
            name="Plano Test",
            billing_cycle=BillingCycleTypeEnum.FIXED,
            duration_minutes=50000  # Mais de 30 dias
        )
        print("❌ Duração muito alta: Deveria ter falhado")
    except Exception as e:
        print("✅ Duração muito alta: Validação funcionando -", str(e))
    
    # Teste 4: Nome vazio (deve falhar)
    try:
        invalid_name = RatePlansCreate(
            hotel_id=hotel_id,
            name="",
            billing_cycle=BillingCycleTypeEnum.NIGHTLY,
            duration_minutes=1440
        )
        print("❌ Nome vazio: Deveria ter falhado")
    except Exception as e:
        print("✅ Nome vazio: Validação funcionando -", str(e))

def test_room_prices_validations():
    """Testa validações do RoomPrices"""
    print("\\n💵 TESTANDO VALIDAÇÕES - ROOM PRICES")
    print("="*50)
    
    room_type_id = uuid4()
    rate_plan_id = uuid4()
    
    # Teste 1: Dados válidos
    try:
        valid_price = RoomPricesCreate(
            room_type_id=room_type_id,
            rate_plan_id=rate_plan_id,
            amount=Decimal("150.00"),
            currency="BRL",
            days_of_week=[1, 2, 3, 4, 5]  # Segunda a Sexta
        )
        print("✅ Dados válidos: OK")
    except Exception as e:
        print(f"❌ Dados válidos: {e}")
    
    # Teste 2: Valor zero (deve falhar)
    try:
        invalid_amount = RoomPricesCreate(
            room_type_id=room_type_id,
            rate_plan_id=rate_plan_id,
            amount=Decimal("0"),
            currency="BRL",
            days_of_week=[1, 2]
        )
        print("❌ Valor zero: Deveria ter falhado")
    except Exception as e:
        print("✅ Valor zero: Validação funcionando -", str(e))
    
    # Teste 3: Moeda inválida (deve falhar)
    try:
        invalid_currency = RoomPricesCreate(
            room_type_id=room_type_id,
            rate_plan_id=rate_plan_id,
            amount=Decimal("100.00"),
            currency="XYZ",
            days_of_week=[1, 2]
        )
        print("❌ Moeda inválida: Deveria ter falhado")
    except Exception as e:
        print("✅ Moeda inválida: Validação funcionando -", str(e))
    
    # Teste 4: Dia da semana inválido (deve falhar)
    try:
        invalid_day = RoomPricesCreate(
            room_type_id=room_type_id,
            rate_plan_id=rate_plan_id,
            amount=Decimal("100.00"),
            currency="BRL",
            days_of_week=[1, 2, 8]  # 8 é inválido
        )
        print("❌ Dia da semana inválido: Deveria ter falhado")
    except Exception as e:
        print("✅ Dia da semana inválido: Validação funcionando -", str(e))
    
    # Teste 5: Lista vazia de dias (deve falhar)
    try:
        empty_days = RoomPricesCreate(
            room_type_id=room_type_id,
            rate_plan_id=rate_plan_id,
            amount=Decimal("100.00"),
            currency="BRL",
            days_of_week=[]
        )
        print("❌ Lista vazia de dias: Deveria ter falhado")
    except Exception as e:
        print("✅ Lista vazia de dias: Validação funcionando -", str(e))
    
    # Teste 6: Dias duplicados (deve remover duplicatas)
    try:
        duplicate_days = RoomPricesCreate(
            room_type_id=room_type_id,
            rate_plan_id=rate_plan_id,
            amount=Decimal("100.00"),
            currency="BRL",
            days_of_week=[1, 2, 2, 3, 3, 3]
        )
        print(f"✅ Dias duplicados: Removeu duplicatas - {duplicate_days.days_of_week}")
    except Exception as e:
        print(f"❌ Dias duplicados: {e}")

def test_enum_consistency():
    """Testa consistência dos enums"""
    print("\\n🔄 TESTANDO CONSISTÊNCIA DOS ENUMS")
    print("="*50)
    
    # Importar enum do modelo
    from models.room_types_model import BillingCycleType
    
    model_values = [e.value for e in BillingCycleType]
    schema_values = [e.value for e in BillingCycleTypeEnum]
    
    print(f"Enum do Model: {model_values}")
    print(f"Enum do Schema: {schema_values}")
    print(f"✅ Consistência: {model_values == schema_values}")

def main():
    """Executa todos os testes de validação"""
    print("🧪 EXECUTANDO TESTES DE VALIDAÇÃO")
    print("=" * 70)
    
    test_room_types_validations()
    test_rate_plans_validations()
    test_room_prices_validations()
    test_enum_consistency()
    
    print("\\n🎯 TESTES CONCLUÍDOS!")
    print("=" * 70)

if __name__ == "__main__":
    main()