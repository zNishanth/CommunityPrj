"""
Django REST Framework Views — catchPhish + ML Integration.
Endpoints:
  POST /api/detect/        – ML phishing detection
  POST /api/report/        – Community report (auth required)
  POST /api/signup/
  GET  /api/stats/
  POST /api/chain-report/  – Record confirmed phishing hash on-chain
"""
import hashlib
import logging
from django.conf import settings
from rest_framework import generics, pagination, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializer import URLSerializer, SignupSerializer, ReportedURLSSerializer, ChainReportSerializer
from .models import ReportedURL
from ml.predictor import predict as ml_predict

logger = logging.getLogger(__name__)


class SignUPView(generics.CreateAPIView):
    serializer_class = SignupSerializer

    def post(self, request):
        data = self.serializer_class(data=request.data)
        if data.is_valid():
            data.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)


class DetectView(generics.GenericAPIView):
    """
    POST { "url": "https://example.com" }
    Returns verdict, confidence, and extracted features.
    """
    serializer_class = URLSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        url = serializer.validated_data["url"]
        result = ml_predict(url)

        # Optionally auto-flag very high confidence phishing
        if result["verdict"] == "Phishing" and result["confidence"] >= 0.90:
            ReportedURL.objects.get_or_create(
                url=url,
                defaults={"confirmed": False},
            )

        return Response(result, status=status.HTTP_200_OK)


class ReportView(generics.GenericAPIView):
    """
    Authenticated endpoint: community member reports a URL.
    POST { "url": "https://phish.example.com" }
    """
    serializer_class = URLSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        url = serializer.validated_data["url"]
        obj, created = ReportedURL.objects.get_or_create(url=url, user=request.user)

        if created:
            return Response({"msg": "Successfully reported"}, status=status.HTTP_201_CREATED)
        return Response({"msg": "Already reported by you"}, status=status.HTTP_200_OK)


class ChainReportView(generics.GenericAPIView):
    """
    Authenticated endpoint: record a phishing URL hash on the blockchain.
    POST { "url": "https://phish.example.com" }

    Calls the PhishRegistry smart contract's `reportPhishing(bytes32 urlHash)`.
    Returns the transaction hash.
    """
    serializer_class = ChainReportSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        url = serializer.validated_data["url"]
        url_hash = "0x" + hashlib.sha256(url.encode()).hexdigest()

        try:
            tx_hash = _submit_to_chain(url_hash)
            # Mark as confirmed in DB too
            ReportedURL.objects.filter(url=url).update(confirmed=True)
            return Response(
                {"url_hash": url_hash, "tx_hash": tx_hash},
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            logger.error("Blockchain submission failed: %s", exc)
            return Response(
                {"error": "Blockchain submission failed", "detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class StatsUserView(generics.ListAPIView):
    queryset = ReportedURL.objects.all().order_by("-reported_date")
    serializer_class = ReportedURLSSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = pagination.PageNumberPagination


# ─── Blockchain helper ────────────────────────────────────────────────────────

def _submit_to_chain(url_hash: str) -> str:
    """
    Submits the URL hash to the PhishRegistry smart contract.
    Reads config from Django settings:
      BLOCKCHAIN_RPC_URL, CONTRACT_ADDRESS, CONTRACT_ABI_PATH, OWNER_PRIVATE_KEY
    Returns the transaction hash string.
    """
    from web3 import Web3
    import json

    rpc_url = getattr(settings, "BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
    contract_address = getattr(settings, "CONTRACT_ADDRESS", "")
    abi_path = getattr(settings, "CONTRACT_ABI_PATH", "contracts/PhishRegistry.json")
    private_key = getattr(settings, "OWNER_PRIVATE_KEY", "")

    if not contract_address or not private_key:
        raise ValueError("BLOCKCHAIN_RPC_URL, CONTRACT_ADDRESS, OWNER_PRIVATE_KEY must be set in settings.")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to blockchain node at {rpc_url}")

    with open(abi_path) as f:
        abi = json.load(f)["abi"]

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address), abi=abi
    )
    account = w3.eth.account.from_key(private_key)

    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.reportPhishing(url_hash).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 200_000,
        "gasPrice": w3.to_wei("20", "gwei"),
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return w3.to_hex(tx_hash)
