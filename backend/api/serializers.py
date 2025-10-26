from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Itinerary, ItineraryItem, BillGroup, Expense, ExpenseSplit # Add new models
import decimal

class UserSimpleSerializer(serializers.ModelSerializer):
    """
    A simple serializer to show user ID and username.
    Used for showing member information in groups.
    """
    class Meta:
        model = User
        fields = ['id', 'username']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Used in the 'Create' (register) endpoint.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # This properly hashes the password
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class ItineraryItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual itinerary items.
    Used for creating, updating, and deleting items.
    """
    class Meta:
        model = ItineraryItem
        fields = ['id', 'description', 'location_name', 'start_time', 'end_time', 'order']
        

class ItineraryItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating itinerary items.
    Includes the itinerary foreign key.
    """
    class Meta:
        model = ItineraryItem
        fields = ['id', 'itinerary', 'description', 'location_name', 'start_time', 'end_time', 'order']


class ItineraryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single itinerary.
    This "nests" the items inside the itinerary.
    Returns items for manual editing OR ai_generated_data for AI-generated itineraries.
    """
    items = ItineraryItemSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Itinerary
        fields = [
            'id', 'owner', 'owner_username', 'title', 'region', 
            'created_at', 'updated_at', 
            'items',  # For future manual editing
            'ai_generated_data'  # The full AI JSON
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']


class ItineraryListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing all itineraries.
    Used in the list view (without nested items for performance).
    """
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = ['id', 'title', 'region', 'owner_username', 'created_at', 'item_count']

    def get_item_count(self, obj):
        return obj.items.count()



class ExpenseSplitSerializer(serializers.ModelSerializer):
    """
    Serializer for the *input* of who owes what.
    """
    # We send the user_id, not the whole user object
    user_owed_id = serializers.IntegerField(write_only=True) 

    class Meta:
        model = ExpenseSplit
        fields = ['user_owed_id', 'amount_owed']


class ExpenseSplitReadSerializer(serializers.ModelSerializer):
    """
    Serializer for *reading* split information.
    Includes both user_owed ID and username for display.
    """
    user_owed = serializers.IntegerField(source='user_owed.id', read_only=True)
    user_owed_username = serializers.CharField(source='user_owed.username', read_only=True)
    
    class Meta:
        model = ExpenseSplit
        fields = ['user_owed', 'user_owed_username', 'amount_owed']


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Expense.
    This is the "nested" serializer.
    """
    # This 'splits' field will accept a *list* of ExpenseSplit objects
    splits = ExpenseSplitSerializer(many=True, write_only=True)
    payer_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'group', 'description', 'total_amount', 'date', 'payer_id', 
            'split_type', 'receipt_image', 'item_data_json', 'splits'
        ]

    def validate(self, data):
        """
        Check that:
        1. The payer exists and is a member of the group
        2. All users in splits exist and are members of the group
        3. The sum of the splits equals the total_amount
        """
        group = data['group']
        payer_id = data['payer_id']
        
        # Check if payer exists
        try:
            payer = User.objects.get(id=payer_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                f"Payer with ID {payer_id} does not exist."
            )
        
        # Check if payer is a member of the group
        if payer not in group.members.all():
            raise serializers.ValidationError(
                f"Payer '{payer.username}' is not a member of this group."
            )
        
        # Check if all users in splits exist and are members
        for split_data in data['splits']:
            user_owed_id = split_data['user_owed_id']
            try:
                user_owed = User.objects.get(id=user_owed_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f"User with ID {user_owed_id} in splits does not exist."
                )
            
            if user_owed not in group.members.all():
                raise serializers.ValidationError(
                    f"User '{user_owed.username}' in splits is not a member of this group."
                )
        
        # Check that the sum of the splits equals the total_amount
        total_split = sum(
            split_data['amount_owed'] for split_data in data['splits']
        )
        total_amount = data['total_amount']

        # Use Decimal for money comparison
        if not decimal.Decimal(total_split).quantize(decimal.Decimal('.01')) == \
               decimal.Decimal(total_amount).quantize(decimal.Decimal('.01')):
            raise serializers.ValidationError(
                f"The sum of splits (${total_split}) does not "
                f"match the total_amount (${total_amount})."
            )
        
        return data

    def create(self, validated_data):
        """
        This is the magic. It creates the Expense AND all its Splits.
        """
        splits_data = validated_data.pop('splits')
        payer_id = validated_data.pop('payer_id')
        
        # Create the parent Expense object
        expense = Expense.objects.create(
            payer_id=payer_id, 
            **validated_data
        )

        # Loop through the split data and create each ExpenseSplit object
        for split_data in splits_data:
            ExpenseSplit.objects.create(
                expense=expense,
                user_owed_id=split_data['user_owed_id'],
                amount_owed=split_data['amount_owed']
            )
            
        return expense


class ExpenseReadSerializer(serializers.ModelSerializer):
    """
    Serializer for *reading* expense information in GET responses.
    Includes payer info, date, and readable splits.
    """
    payer = serializers.IntegerField(source='payer.id', read_only=True)
    payer_username = serializers.CharField(source='payer.username', read_only=True)
    splits_read = ExpenseSplitReadSerializer(source='splits', many=True, read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'group', 'description', 'total_amount', 'date',
            'payer', 'payer_username', 'split_type', 'receipt_image', 
            'item_data_json', 'splits_read'
        ]


class BillGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for a list of BillGroups.
    Now includes member IDs and usernames.
    """
    # Use the simple serializer for members, make it read-only
    members = UserSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = BillGroup
        # The 'members' field passed during creation is handled in the ViewSet
        fields = ['id', 'name', 'members', 'created_at']


class BillGroupDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for one BillGroup, showing members (with IDs) and expenses.
    """
    # Use the simple serializer here too
    members = UserSimpleSerializer(many=True, read_only=True)
    
    # Show all expenses with full details including payer info and splits
    expenses = ExpenseReadSerializer(many=True, read_only=True) 

    class Meta:
        model = BillGroup
        fields = ['id', 'name', 'members', 'created_at', 'expenses']
