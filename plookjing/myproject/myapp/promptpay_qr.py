import libscrc
import qrcode # For generating QR code images
from PIL import Image # Pillow library, a dependency of qrcode
import io # For handling in-memory image data
from IPython.display import display, Image as IPImage # For displaying images in Jupyter
from typing import Union, Optional

# --- EMVCo Tag Constants ---
TAG_PAYLOAD_FORMAT_INDICATOR = "00"
TAG_POINT_OF_INITIATION_METHOD = "01"
TAG_MERCHANT_ACCOUNT_INFORMATION = "29"
# Sub-tags for Merchant Account Information (Tag 29 - PromptPay specific context)
SUB_TAG_AID_PROMPTPAY = "00"
SUB_TAG_MOBILE_NUMBER_PROMPTPAY = "01"
SUB_TAG_NATIONAL_ID_PROMPTPAY = "02"

TAG_TRANSACTION_CURRENCY = "53"
TAG_TRANSACTION_AMOUNT = "54" # Optional if amount is zero or not specified
TAG_COUNTRY_CODE = "58"
TAG_CRC = "63"

# --- Standard Values ---
VALUE_PAYLOAD_FORMAT_INDICATOR = "01"    # Version 1 of the EMVCo QR standard
VALUE_POINT_OF_INITIATION_MULTIPLE = "11" # Static QR for multiple uses
VALUE_POINT_OF_INITIATION_ONETIME = "12"  # QR for one-time use
VALUE_PROMPTPAY_AID = "A000000677010111" # Specific AID for PromptPay
VALUE_COUNTRY_CODE_TH = "TH"             # Thailand
VALUE_CURRENCY_THB = "764"               # Thai Baht (ISO 4217 numeric)

# --- Fixed Lengths for Certain Field Values or LL part of TLV ---
LEN_CRC_VALUE_HEX = "04" # Length of the CRC value itself (4 hex characters)

class QRError(Exception):
    """Custom base exception for QR generation errors."""
    pass

class InvalidInputError(QRError):
    """Custom exception for invalid input values."""
    pass

def _format_tlv(tag: str, value: str) -> str:
    """
    Formats a Tag-Length-Value (TLV) string.
    The length is a 2-digit zero-padded string representing the byte length of the value.
    """
    if not isinstance(value, str):
        raise TypeError(f"TLV value for tag {tag} must be a string, got {type(value)}.")
    length_str = f"{len(value):02d}"
    return f"{tag}{length_str}{value}"

def calculate_crc(code_string: str) -> str:
    """
    Calculates the CRC16 (CCITT-FALSE variant) for the given code string.
    `libscrc.ccitt_false` uses poly=0x1021, init=0xFFFF, refin=False, refout=False, xorout=0x0000.
    This matches the common requirement for EMVCo QR CRC.
    """
    try:
        encoded_string = str.encode(code_string, 'ascii')
    except UnicodeEncodeError:
        raise InvalidInputError("Payload contains non-ASCII characters, which is not supported for CRC calculation.")

    crc_val = libscrc.ccitt_false(encoded_string) # type: ignore
    crc_hex_str = hex(crc_val)[2:].upper() # Remove "0x" and uppercase
    return crc_hex_str.rjust(4, '0') # Zero-pad to 4 characters

def generate_promptpay_qr_payload(
    mobile: Optional[str] = None,
    nid: Optional[str] = None,
    amount: Optional[Union[float, int, str]] = None,
    one_time: bool = False
) -> str:
    """
    Generates the full PromptPay QR code payload string according to EMVCo standards.
    (Adapted from the Chalice app's logic)
    """
    if not mobile and not nid:
        raise InvalidInputError("Either mobile number or National ID (NID) must be provided.")
    if mobile and nid:
        raise InvalidInputError("Provide either mobile number or National ID (NID), not both.")

    payload_elements = []

    # Tag 00: Payload Format Indicator
    payload_elements.append(
        _format_tlv(TAG_PAYLOAD_FORMAT_INDICATOR, VALUE_PAYLOAD_FORMAT_INDICATOR)
    )

    # Tag 01: Point of Initiation Method
    initiation_method_value = VALUE_POINT_OF_INITIATION_ONETIME if one_time else VALUE_POINT_OF_INITIATION_MULTIPLE
    payload_elements.append(
        _format_tlv(TAG_POINT_OF_INITIATION_METHOD, initiation_method_value)
    )

    # Tag 29: Merchant Account Information
    merchant_account_sub_elements = []
    merchant_account_sub_elements.append(_format_tlv(SUB_TAG_AID_PROMPTPAY, VALUE_PROMPTPAY_AID))

    if mobile:
        mobile_cleaned = mobile.strip()
        if not (len(mobile_cleaned) == 10 and mobile_cleaned.isdigit()):
            raise InvalidInputError("Mobile number must be a 10-digit string (e.g., '0812345678').")
        formatted_mobile_value = f"00{VALUE_COUNTRY_CODE_TH}{mobile_cleaned[1:]}"
        merchant_account_sub_elements.append(
            _format_tlv(SUB_TAG_MOBILE_NUMBER_PROMPTPAY, formatted_mobile_value)
        )
    elif nid:
        nid_cleaned = nid.strip().replace('-', '')
        if not (len(nid_cleaned) == 13 and nid_cleaned.isdigit()):
            raise InvalidInputError("National ID (NID) must be a 13-digit string (e.g., '1234567890123').")
        merchant_account_sub_elements.append(
            _format_tlv(SUB_TAG_NATIONAL_ID_PROMPTPAY, nid_cleaned)
        )
    payload_elements.append(
        _format_tlv(TAG_MERCHANT_ACCOUNT_INFORMATION, "".join(merchant_account_sub_elements))
    )

    # Tag 53: Transaction Currency (THB)
    payload_elements.append(
        _format_tlv(TAG_TRANSACTION_CURRENCY, VALUE_CURRENCY_THB)
    )

    # Tag 54: Transaction Amount (Optional)
    if amount is not None:
        amount_str_eval = str(amount).strip()
        if amount_str_eval:
            try:
                amount_float = float(amount_str_eval)
                if amount_float != 0.0:
                    if amount_float < 0:
                        raise InvalidInputError("Transaction amount cannot be negative.")
                    formatted_amount_value = f"{amount_float:.2f}"
                    payload_elements.append(_format_tlv(TAG_TRANSACTION_AMOUNT, formatted_amount_value))
            except ValueError:
                raise InvalidInputError(f"Invalid amount value: '{amount}'. Must be a number.")

    # Tag 58: Country Code (TH)
    payload_elements.append(
        _format_tlv(TAG_COUNTRY_CODE, VALUE_COUNTRY_CODE_TH)
    )

    # --- CRC Calculation ---
    data_for_crc_calculation = "".join(payload_elements)
    string_to_calculate_crc_on = data_for_crc_calculation + TAG_CRC + LEN_CRC_VALUE_HEX
    crc_hex_value = calculate_crc(string_to_calculate_crc_on)
    final_payload_string = string_to_calculate_crc_on + crc_hex_value
    return final_payload_string.upper()

def display_promptpay_qr(
    mobile: Optional[str] = None,
    nid: Optional[str] = None,
    amount: Optional[Union[float, int, str]] = None,
    one_time: bool = False,
    box_size: int = 10,
    border: int = 4
):
    """
    Generates a PromptPay QR payload, creates a QR image, and displays it in Jupyter.

    Args:
        mobile: 10-digit Thai mobile number.
        nid: 13-digit Thai National ID or Tax ID.
        amount: The transaction amount.
        one_time: If True, QR is for single use. Defaults to False.
        box_size: Controls how many pixels each “box” of the QR code is.
        border: Controls how many boxes thick the border should be (the default is 4,
                which is the minimum according to the specs).
    """
    try:
        # 1. Generate the QR payload string
        payload = generate_promptpay_qr_payload(mobile=mobile, nid=nid, amount=amount, one_time=one_time)
        print(f"Generated Payload: {payload}") # Optional: print payload for verification

        # 2. Create QR code image object
        qr_img = qrcode.QRCode(
            version=None, # Let the library choose the version
            error_correction=qrcode.constants.ERROR_CORRECT_M, # Medium error correction
            box_size=box_size,
            border=border,
        )
        qr_img.add_data(payload)
        qr_img.make(fit=True)

        img = qr_img.make_image(fill_color="black", back_color="white")

        # 3. Save image to an in-memory buffer
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # 4. Display the image in Jupyter Notebook
        display(IPImage(data=img_byte_arr))

    except QRError as e:
        print(f"Error generating QR code: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")