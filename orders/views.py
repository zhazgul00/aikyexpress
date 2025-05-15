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

        print(f"\n--- INSIDE OrderViewSet.get_queryset ---")
        print(f"User: {user}, User Role: {getattr(user, 'role', 'N/A')}")
        print(f"Query Params (from Flutter): {self.request.query_params}")
        print(f"Applied Status Filter: {status_filter}")

        all_user_orders_qs = Order.objects.none()

        if hasattr(user, 'role'):
            if user.role == 'store':
                try:
                    store = Store.objects.get(user=user)
                    all_user_orders_qs = Order.objects.filter(store=store).order_by('-created_at')
                    print(f"Store user: {user.username}, found store: Store ID {store.id}")
                    all_ids = list(all_user_orders_qs.values_list('id', 'status', 'product__id')) # Добавил статус и product_id для отладки
                    print(f"ALL Orders for this store BEFORE status filter (ID, Status, ProductID): {all_ids}")
                except Store.DoesNotExist:
                    print(f"Store user: {user.username}, Store.DoesNotExist - returning no orders.")
                    return Order.objects.none()
            # ... (другие роли, если нужны) ...
            else:
                print(f"User {user.username} has an unknown role '{getattr(user, 'role', 'N/A')}' or no orders for this role.")
                return Order.objects.none()
        else:
            print(f"User {user.username} has no 'role' attribute - returning no orders.")
            return Order.objects.none()

        final_qs = all_user_orders_qs
        if status_filter:
            final_qs = all_user_orders_qs.filter(status=status_filter)
            print(f"Applied status filter '{status_filter}'.")
            filtered_ids = list(final_qs.values_list('id', 'status', 'product__id'))
            print(f"Order IDs for this store AFTER status filter '{status_filter}' (ID, Status, ProductID): {filtered_ids}")

        print(f"Final queryset count for user {user.username}: {final_qs.count()}")
        print(f"--- END OF OrderViewSet.get_queryset ---\n")
        return final_qs

    # ... (метод deliver и perform_create (который не должен вызываться) остаются как есть) ...
    def perform_create(self, serializer):
        print("WARNING: OrderViewSet.perform_create called. This should ideally go through /create/ endpoint.")
        return Response({"error": "Please use the /create/ endpoint to create orders."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['patch'])
    def deliver(self, request, pk=None):
        # ... (код метода deliver) ...
        user = request.user
        if not hasattr(user, 'role') or user.role != 'driver':
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        try:
            order = self.get_object()
            driver_profile = Driver.objects.get(user=user)
            if order.driver != driver_profile:
                return Response({"error": "This is not your order."}, status=status.HTTP_403_FORBIDDEN)
            order.status = 'delivered'
            order.save()
            return Response({"message": "Order marked as delivered"})
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Driver.DoesNotExist:
            return Response({"error": "Driver profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Error updating order status."}, status=status.HTTP_400_BAD_REQUEST)