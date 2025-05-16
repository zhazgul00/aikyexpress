from rest_framework import viewsets, status, serializers # serializers может понадобиться для ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from warehouses.models import Product, Warehouse
from stores.models import Store
from drivers.models import Driver
from .serializers import OrderSerializer, CreateOrderSerializer



class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(f"\n--- INSIDE CreateOrderView.post ---")
        print(f"Authenticated User: {self.request.user}, User Role: {getattr(self.request.user, 'role', 'N/A')}")
        print(f"Raw Request Data (from Flutter): {self.request.data}")

        if not hasattr(request.user, 'role') or request.user.role != 'store':
            return Response({'error': 'Только магазины могут создавать заказы'}, status=status.HTTP_403_FORBIDDEN)

        current_store = None
        try:
            current_store = Store.objects.get(user=request.user)
            # ИСПРАВЛЕНО: Выводим username связанного пользователя
            print(f"DEBUG (CreateOrderView): Found store for user '{request.user.username}': Store ID {current_store.id}, Address: {current_store.address}")
        except Store.DoesNotExist:
            print(f"ERROR (CreateOrderView): Store profile not found for user {request.user}")
            return Response({'error': 'Профиль магазина не найден'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            print(f"DEBUG (CreateOrderView): CreateOrderSerializer Validated Data: {serializer.validated_data}")
            validated_data = serializer.validated_data
            product_instance = validated_data.get('product') # Это экземпляр Product
            order_quantity = validated_data.get('quantity')

            # Проверка наличия имени у продукта перед использованием в сообщении об ошибке
            product_display_name = product_instance.name if hasattr(product_instance, 'name') else f"Product ID {product_instance.id}"

            if product_instance.quantity < order_quantity:
                print(f"ERROR (CreateOrderView): Not enough stock for product {product_display_name}")
                return Response(
                    {'error': f'Недостаточно товара "{product_display_name}" на складе. Доступно: {product_instance.quantity}, Запрошено: {order_quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # Опционально: обернуть в транзакцию, если у вас несколько операций с БД
                # from django.db import transaction
                # with transaction.atomic():
                product_instance.quantity -= order_quantity
                product_instance.save()
                print(f"DEBUG (CreateOrderView): Stock updated for product {product_instance.id}. New quantity: {product_instance.quantity}")

                order = serializer.save(store=current_store, status='new')
                print(f"УСПЕХ (CreateOrderView): Заказ успешно создан: Order ID {order.id}, Product ID {order.product_id}, Store ID: {order.store_id}, Status: {order.status}")

                check_order_exists = Order.objects.filter(id=order.id, store=current_store).exists()
                print(f"DEBUG (CreateOrderView): CHECK - Order {order.id} exists in DB for store {current_store.id} immediately after save: {check_order_exists}")

                if not check_order_exists:
                    print(f"CRITICAL (CreateOrderView): Order {order.id} was supposedly saved but not found for store {current_store.id} immediately after!")

                response_serializer = OrderSerializer(order, context={'request': request}) # Передаем request в контекст
                return Response({'message': 'Заказ успешно создан', 'order': response_serializer.data}, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(f"ERROR (CreateOrderView): Exception during product stock update or order save: {e}")
                import traceback
                traceback.print_exc()
                return Response({'error': 'Произошла ошибка при сохранении заказа или обновлении остатков.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(f"ERROR (CreateOrderView): CreateOrderSerializer Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status', None)
        qs = Order.objects.none() # Инициализируем qs как пустой

        print(f"\n--- INSIDE OrderViewSet.get_queryset ---")
        print(f"User: {user.username}, User Role: {getattr(user, 'role', 'N/A')}") # Используем user.username
        print(f"Query Params (from Flutter): {self.request.query_params}")
        print(f"Applied Status Filter: {status_filter}")

        if hasattr(user, 'role'):
            role = user.role
            if role == 'store':
                try:
                    store = Store.objects.get(user=user)
                    qs = Order.objects.filter(store=store).order_by('-created_at')
                    print(f"Store user: {user.username}, found store: Store ID {store.id}")
                    # ... (остальные print для store, если нужны)
                except Store.DoesNotExist:
                    print(f"Store user: {user.username}, Store.DoesNotExist for this user.")
                    # qs уже Order.objects.none(), так что ничего не делаем
            elif role == 'driver':
                try:
                    driver = Driver.objects.get(user=user)
                    qs = Order.objects.filter(driver=driver).order_by('-created_at')
                    print(f"Driver user: {user.username}, found driver: Driver ID {driver.id}")
                except Driver.DoesNotExist:
                    print(f"Driver user: {user.username}, Driver.DoesNotExist for this user.")
            elif role == 'warehouse':
                print(f"DEBUG: User role is 'warehouse'. Attempting to find Warehouse profile for {user.username}...")
                try:
                    warehouse_profile = Warehouse.objects.get(user=user) # Переименовал для ясности
                    print(f"Found Warehouse Profile: ID {warehouse_profile.id}, Company: {getattr(warehouse_profile, 'company_name', 'N/A')} for user {user.username}")
                    qs = Order.objects.filter(product__warehouse=warehouse_profile).order_by('-created_at')

                    all_orders_data = [{
                        "order_id": o.id, "order_status": o.status, "product_id": o.product_id,
                        "product_name": o.product.name, "product_warehouse_id": o.product.warehouse_id
                    } for o in qs]
                    print(f"ALL Orders for Warehouse ID {warehouse_profile.id} (User: {user.username}): {all_orders_data}")
                    print(f"Count of orders found for this warehouse: {qs.count()}")

                except Warehouse.DoesNotExist:
                    # ЭТО СООБЩЕНИЕ ДОЛЖНО ВЫВЕСТИСЬ, ЕСЛИ ПРОФИЛЯ НЕТ
                    print(f"CRITICAL (get_queryset): Warehouse.DoesNotExist for user {user.username} (ID: {user.id}) with role 'warehouse'. No orders will be returned.")
                    # qs уже Order.objects.none()
                except Exception as e:
                    print(f"EXCEPTION (get_queryset) for warehouse user {user.username}: {type(e).__name__} - {e}")
                    import traceback
                    traceback.print_exc()
                    # qs уже Order.objects.none()
            else:
                # Этот блок выполнится, если роль есть, но она не 'store', 'driver' или 'warehouse'
                print(f"User {user.username} has an UNHANDLED role: '{role}'. No orders will be returned.")
        else:
            print(f"User {user.username} has no 'role' attribute. No orders will be returned.")

        # Фильтрация по статусу применяется к тому qs, который был сформирован выше
        if status_filter and qs.exists(): # Применяем фильтр, только если qs не пустой
            print(f"Attempting to apply status filter '{status_filter}' to {qs.count()} orders...")
            qs = qs.filter(status=status_filter)
            print(f"Orders count after status filter '{status_filter}': {qs.count()}")
        elif status_filter:
            print(f"Status filter '{status_filter}' provided, but no initial orders found to filter.")


        print(f"Final queryset count for user {user.username} before returning: {qs.count()}")
        print(f"--- END OF OrderViewSet.get_queryset ---\n")
        return qs

    # ... (остальные методы OrderViewSet) ...