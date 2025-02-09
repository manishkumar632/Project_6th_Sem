from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from mongo_utils import db
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from decouple import config
from django.contrib.auth.hashers import make_password


users_collection = db['Users']
blacklisted_tokens_collection = db['BlacklistedTokens']

def Home(request):
    users = users_collection.find()
    user_list = list(users)
    for user in user_list:
        user['_id'] = str(user['_id'])

    return JsonResponse(user_list, safe=False)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "email": user.email,
            "username": user.username,
            "bio": user.bio,
            "profileImage": user.profileImage,
            "gender": user.gender,
        }
        return Response(data)

class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        # password length should be at least 6 characters
        if len(password) < 6:
            return Response({"error": "Password should be at least 6 characters."}, status=status.HTTP_400_BAD_REQUEST)
        if not email or not username:
            return Response({"error": "Email and username are required."}, status=status.HTTP_400_BAD_REQUEST)
        if users_collection.find_one({"email": email}):  # Check if email already exists
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        if users_collection.find_one({"username": username}):  # Check if username already exists
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
        # Deserialize the request data to validate it
        serializer = UserSerializer(data=request.data)
        
        # Hash the password before saving
        if serializer.is_valid():
            # Extract validated data from the serializer
            user_data = serializer.validated_data
            hashed_password = make_password(user_data["password"])
            
            # Prepare the user data to be inserted into MongoDB
            user = {
                "email": user_data["email"],
                "username": user_data["username"],
                "bio": user_data.get("bio", ""),
                "profileImage": user_data.get("profileImage", config('DEFAULT_PROFILE_IMAGE')),
                "gender": user_data.get("gender", "M"),
                "password": hashed_password,  # Hashing the password before saving
            }

            try:
                # Insert the user data into the 'Users' collection in MongoDB
                result = users_collection.insert_one(user)
                user["_id"] = str(result.inserted_id)  # Add the generated _id from MongoDB to the response

                return Response(
                    {
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "bio": user_data.get("bio", ""),
                        "profileImage": user_data.get("profileImage", ""),
                        "gender": user_data.get("gender", "M"),
                        "message": "User registered successfully",
                        "_id": user["_id"],  # Include the MongoDB _id in the response
                    },
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response(
                    {"error": f"An error occurred: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Helper function to generate tokens
def generate_tokens_for_user(user):
    refresh_token = jwt.encode(
        {"id": str(user["_id"]), "email": user["email"], "exp": datetime.now(timezone.utc) + timedelta(days=7)},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    
    access_token = jwt.encode(
        {"id": str(user["_id"]), "email": user["email"], "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    
    return {
        "refresh": refresh_token,
        "access": access_token,
    }

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch user from MongoDB
        user = users_collection.find_one({"email": email})

        if user and check_password(password, user["password"]):  # Verifying hashed password
            tokens = generate_tokens_for_user(user)
            return Response({
                "username": user["username"],
                "profileImage": user.get("profileImage", ""),
                "gender": user.get("gender", "M"),
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the refresh token to verify and get the user info
            decoded_payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            print(decoded_payload)
            exp = decoded_payload["exp"]  # Expiry timestamp of the token

            user = users_collection.find_one({"email": decoded_payload["email"]})
            isTokenExpire = blacklisted_tokens_collection.find_one({"refresh_token": refresh_token})
            if not user:
                return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
            if isTokenExpire:
                return Response({"error": "This refresh token has been blacklisted. Please log in again."}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Add the refresh token to the blacklist
            blacklisted_tokens_collection.insert_one({
                "refresh_token": refresh_token,
                "user_id": decoded_payload["id"],
                "expires_at": datetime.fromtimestamp(exp, timezone.utc)
                })
            current_time = datetime.now(timezone.utc)
            blacklisted_tokens_collection.delete_many({"expires_at": {"$lt": current_time}})
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        
        except jwt.ExpiredSignatureError:
            return Response({"error": "Refresh token expired."}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)


# Create Blog View
# Requirements:
# 1. User should be authenticated
# Before saving the blog, To the following:
    # 1. Check if the Title is unique
    # 2. Extract the image from <img /> and store it to cloudinary and replace the image src with the cloudinary url
    # 3. Assign date to the blog
    # 4. Assign the user id to the blog 
    # 5. Save the blog to the database

    
