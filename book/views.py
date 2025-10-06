# views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.conf import settings
from .models import BookProject
from .serializers import BookProjectSerializer
import logging

logger = logging.getLogger(__name__)


class UploadBookProjectView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data.copy()
        cover_file = request.FILES.get('cover_file')
        cover_description = data.get('cover_description')
        is_cover_expert = data.get('is_cover_expert', False)

        if not cover_file and not cover_description:
            return Response({
                'status': 'error',
                'message': 'Please provide either a cover file or a cover description.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookProjectSerializer(data=data)

        if serializer.is_valid():
            try:
                book_project = serializer.save(user=request.user)
                if is_cover_expert:
                    self.send_cover_expert_email(request, book_project)
                return Response({
                    'status': 'success',
                    'message': 'Book project uploaded successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error("Error saving BookProject", exc_info=True)
                return Response({
                    'status': 'error',
                    'message': 'An error occurred while saving the project.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning("Validation error: %s", serializer.errors)
            return Response({
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class SaveOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data.copy()

        cover_file = request.FILES.get('cover_file')
        cover_description = data.get('cover_description')
        
        if not cover_file and not cover_description:
            return Response({
                'status': 'error',
                'message': 'Please provide either a cover file or a cover description.'
            }, status=status.HTTP_400_BAD_REQUEST)

        def norm_money(val):
            try:
                if val is None or val == "":
                    return None
                return f"{float(val):.2f}"
            except Exception:
                return None

        for key in ['shipping_rate', 'tax', 'product_price', 'subtotal']:
            if key in data:
                data[key] = norm_money(data.get(key))

        # ✅ CRITICAL FIX: Mark as 'paid' once saved in /shop
        data['order_status'] = 'paid'  # ← This is the ONLY change

        serializer = BookProjectSerializer(data=data)
        if serializer.is_valid():
            try:
                project = serializer.save(user=request.user)
                return Response({
                    'status': 'success',
                    'message': 'Order saved successfully.',
                    'data': BookProjectSerializer(project).data
                }, status=status.HTTP_201_CREATED)
            except Exception:
                logger.error("Error saving combined order", exc_info=True)
                return Response({
                    'status': 'error',
                    'message': 'An error occurred while saving the order.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning("Validation error (save order): %s", serializer.errors)
            return Response({
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def send_cover_expert_email(self, request, book_project):
        try:
            subject = 'New Cover Expert Request Submission'
            message = f"""
            New Cover Expert Request Received:
            
            Project Details:
            - Title: {book_project.title}
            - Category: {book_project.category}
            - Language: {book_project.language}
            - Page Count: {book_project.page_count}
            - Binding Type: {book_project.binding_type}
            - Cover Finish: {book_project.cover_finish}
            - Interior Color: {book_project.interior_color}
            - Paper Type: {book_project.paper_type}
            - Trim Size: {book_project.trim_size}
            
            Contact Information:
            - Name: {request.data.get('contact_name', 'Not provided')}
            - Email: {request.data.get('contact_email', 'Not provided')}
            - Book Title: {request.data.get('book_title', 'Not provided')}
            - Book Genre: {request.data.get('book_genre', 'Not provided')}
            
            Cover Description:
            {request.data.get('cover_description', 'No description provided')}
            
            The PDF file has been uploaded to the system and is available for review.
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['zeeshanzahid663@gmail.com'],
                fail_silently=False,
            )
            logger.info("Cover expert email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send cover expert email: {str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_books(request):
    try:
        books = BookProject.objects.filter(user=request.user).order_by('-created_at')
        serializer = BookProjectSerializer(books, many=True)
        return Response({
            'status': 'success',
            'results': len(serializer.data),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Failed to fetch user's book projects", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'Failed to fetch your book projects.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_unpaid_projects(request):
    try:
        books = BookProject.objects.filter(user=request.user, order_status='draft').order_by('-created_at')
        serializer = BookProjectSerializer(books, many=True)
        return Response({
            'status': 'success',
            'results': len(serializer.data),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Failed to fetch user's unpaid projects", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'Failed to fetch your unpaid projects.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_paid_orders(request):
    try:
        books = BookProject.objects.filter(user=request.user, order_status='paid').order_by('-created_at')
        serializer = BookProjectSerializer(books, many=True)
        return Response({
            'status': 'success',
            'results': len(serializer.data),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Failed to fetch user's paid orders", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'Failed to fetch your paid orders.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def book_detail(request, pk):
    try:
        book = BookProject.objects.get(pk=pk, user=request.user)
    except BookProject.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Book project not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = BookProjectSerializer(book)
    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_book(request, pk):
    try:
        book = BookProject.objects.get(pk=pk, user=request.user)
    except BookProject.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Book project not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == 'PATCH'
    serializer = BookProjectSerializer(book, data=request.data, partial=partial)

    cover_file = request.FILES.get('cover_file')
    cover_description = request.data.get('cover_description') or book.cover_description

    if not cover_file and not cover_description:
        return Response({
            'status': 'error',
            'message': 'Please provide either a cover file or a cover description.'
        }, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        try:
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Book project updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error updating BookProject", exc_info=True)
            return Response({
                'status': 'error',
                'message': 'An error occurred while updating the project.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.warning("Validation error on update: %s", serializer.errors)
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_book(request, pk):
    try:
        book = BookProject.objects.get(pk=pk, user=request.user)
        book.delete()
        return Response({
            'status': 'success',
            'message': 'Book project deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)
    except BookProject.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Book project not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error("Error deleting BookProject", exc_info=True)
        return Response({
            'status': 'error',
            'message': 'An error occurred while deleting the project.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_all_orders(request):
    if not request.user.is_staff:
        return Response({"detail": "Not authorized."}, status=403)

    orders = BookProject.objects.filter(order_status='paid').order_by("-created_at")
    data = []
    for order in orders:
        data.append({
            "id": order.id,
            "title": order.title,
            "user_email": order.user.email,
            "category": order.category,
            "language": order.language,
            "page_count": order.page_count,
            "created_at": order.created_at,
            "binding_type": order.binding_type,
            "cover_finish": order.cover_finish,
            "interior_color": order.interior_color,
            "paper_type": order.paper_type,
            "trim_size": order.trim_size,
            "pdf_file": order.pdf_file.url if order.pdf_file else None,
            "cover_file": order.cover_file.url if order.cover_file else None,
            "cover_description": order.cover_description,
            "first_name": order.first_name,
            "last_name": order.last_name,
            "company": order.company,
            "address": order.address,
            "apt_floor": order.apt_floor,
            "country": order.country,
            "state": order.state,
            "city": order.city,
            "postal_code": order.postal_code,
            "phone_number": order.phone_number,
            "account_type": order.account_type,
            "has_resale_cert": order.has_resale_cert,
            "shipping_rate": order.shipping_rate,
            "tax": order.tax,
            "courier_name": order.courier_name,
            "estimated_delivery": order.estimated_delivery,
            "selected_service": order.selected_service,
            "product_quantity": order.product_quantity,
            "product_price": order.product_price,
            "subtotal": order.subtotal,
        })

    return Response({
        "status": "success",
        "results": len(data),
        "data": data
    })