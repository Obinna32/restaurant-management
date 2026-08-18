from rest_framework import serializers
from .models import Table, Reservation

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    table_number = serializers.IntergerField(source='table.table_number', read_only=True, allow_null=True)

    class Meta:
        model = Reservation
        fields = (
            'id',
            'customer',
            'customer_username',
            'table',
            'table_number',
            'guest_count',
            'reservation_date',
            'reservation_time',
            'status',
            'special_requests',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('customer', 'status')

    def validate(self, attrs):
        table = attrs.get('table')
        guest_count = attrs.get('guest_count')
        res_date = attrs.get('reservation_date')
        res_time = attrs.get('reservation_time')

        #check table capacity if table is assigned
        if table and guest_count:
            if guest_count > table.capacity:
                raise serializers.ValidationError({
                    'guest_count': f"Selected Table {table.table_number} only has a capacity of {table.capacity} guests."
                })

        #Double-booking validation if table is assigned
        if table and res_date and res_time:
            query = Reservation.objects.filter(
                table=table,
                reservation_date = res_date,
                reservation_time = res_time,
                status__in = ['PENDING', 'CONFIRMED']
            )
            #exclude current instance if updating
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise serializers.ValidationError({
                    'table': f"Table {table.table_number} is already reserved for this date and time."
                })
        return attrs