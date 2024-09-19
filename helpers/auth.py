import streamlit as st
import asyncio

from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth import oauth2

oauthCredentials = st.secrets["oauth"]
CLIENT_ID = oauthCredentials["CLIENT_ID"]
CLIENT_SECRET = oauthCredentials["CLIENT_SECRET"]
REDIRECT_URI = oauthCredentials["REDIRECT_URI"]

client = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)


async def getAuthUrl(client: GoogleOAuth2, redirect_uri: str):
    authorization_url = await client.get_authorization_url(
        redirect_uri, scope=["profile", "email"]
    )
    return authorization_url


async def getAccessToken(client: GoogleOAuth2, redirect_uri: str, code: str):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def getUserIdAndEmail(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def displayLoginButton():
    authorization_url = asyncio.run(getAuthUrl(client, REDIRECT_URI))
    #     components.html(f"""
    # <div style="display: flex; justify-content: left;">
    #     <a href="{authorization_url}" target="_self" style="background-color: {'#fff'}; color: {'#000'}; text-decoration: none; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; padding: 8px 12px; border-radius: 4px; display: flex; align-items: center; font-family: 'Roboto', sans-serif; font-weight: 700;">
    #         <img src="https://lh3.googleusercontent.com/COxitqgJr1sJnIDe8-jiKhxDx1FrYbtRHKJ9z_hELisAlapwE9LUPh6fcXIfb5vwpbMl4xl9H9TRFPc5NOO8Sb3VSgIBrfRYvW6cUA" alt="Google logo" style="margin-right: 8px; width: 26px; height: 26px; background-color: white; border: 2px solid white; border-radius: 4px;">
    #         Sign in with Google
    #     </a>
    # </div>
    # """)
    #     return
    st.write(
        f"""
<div style="display: flex; justify-content: left;">
    <a href="{authorization_url}" target="_blank" style="background-color: {'#fff'}; color: {'#000'}; text-decoration: none; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; padding: 8px 12px; border-radius: 4px; display: flex; align-items: center;">
        <img src="https://lh3.googleusercontent.com/COxitqgJr1sJnIDe8-jiKhxDx1FrYbtRHKJ9z_hELisAlapwE9LUPh6fcXIfb5vwpbMl4xl9H9TRFPc5NOO8Sb3VSgIBrfRYvW6cUA" alt="Google logo" style="margin-right: 8px; width: 26px; height: 26px; background-color: white; border: 2px solid white; border-radius: 4px;">
        Sign in with Google
    </a>
</div>
""",
        unsafe_allow_html=True,
    )


def getUserEmail() -> str | None:
    try:
        code = st.query_params.code
        # Ensure the code is properly extracted from the query params
        # code = code[0]  # Assuming code comes as a list
        token = asyncio.run(getAccessToken(client, REDIRECT_URI, code))
        user_id, user_email = asyncio.run(
            getUserIdAndEmail(client, token["access_token"])
        )
        return user_email
    except (AttributeError, oauth2.GetAccessTokenError):
        return None
