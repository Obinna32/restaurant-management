from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.authentication.models import UserRole
from apps.authentication.permissions import IsStaffOrAdmin, IsAdmin
from .models import Table, Reservation
from .serializers import TableSerializer, ReservationSerializer

# Create your views here.
class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.CHEF]:
            return Reservation.objects.all()
        return Reservation.objects.filter(customer=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsStaffOrAdmin])
    def update_status(self, request, pk=None):
        """Action for staff to confirm, complete, or cancel reservations."""
        reservation = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED']:
            return Response(
                {'error': 'Invalid status provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = new_status
        reservation.save()

        return Response({
            'message': f'Reservation status updated to {new_status}.',
            'reservation': ReservationSerializer(reservation).data
        })