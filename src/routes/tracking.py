from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests
import logging
import json
from enhanced_stealth_scraper import get_enhanced_stealth_tracking

logger = logging.getLogger(__name__)

tracking_bp = Blueprint('tracking', __name__)

# WooCommerce configuration
WOOCOMMERCE_URL = "https://shop.humanfoodbar.com"
WOOCOMMERCE_CONSUMER_KEY = "ck_e796b39727d0a0717194131cc4218eeea6dd43cd"
WOOCOMMERCE_CONSUMER_SECRET = "cs_f7aa55b988e4cc3fefe3c86da06bf45d9fd36574"

@tracking_bp.route('/track-order', methods=['POST'])
@cross_origin()
def track_order():
    """
    Track order with both WooCommerce status and enhanced tracking
    """
    try:
        data = request.get_json()
        order_number = data.get('order_number', '').strip()
        
        if not order_number:
            return jsonify({
                'success': False,
                'error': 'Order number is required'
            }), 400
        
        # Get order from WooCommerce
        order = get_woocommerce_order(order_number)
        
        if not order:
            return jsonify({
                'success': False,
                'error': f'Order {order_number} not found'
            }), 404
        
        # Extract order information
        order_status = order.get('status', 'unknown').upper()
        order_date = order.get('date_created', '')
        
        # Extract tracking information from WooCommerce Shipment Tracking plugin
        tracking_number = None
        tracking_provider = None
        
        meta_data = order.get('meta_data', [])
        for meta in meta_data:
            key = meta.get('key', '')
            if key == '_wc_shipment_tracking_items':
                try:
                    value = meta.get('value', [])
                    # Handle both string (JSON) and list formats
                    if isinstance(value, str):
                        tracking_items = json.loads(value)
                    elif isinstance(value, list):
                        tracking_items = value
                    else:
                        tracking_items = []
                        
                    if tracking_items and len(tracking_items) > 0:
                        tracking_item = tracking_items[0]
                        tracking_number = tracking_item.get('tracking_number', '').strip()
                        tracking_provider = tracking_item.get('tracking_provider', '').strip()
                        if tracking_number:
                            logger.info(f"Found WC tracking: {tracking_number} via {tracking_provider}")
                            break
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Error parsing WC tracking data: {e}")
                    continue
        
        # Backup: Check for RouteApp tracking number
        if not tracking_number:
            for meta in meta_data:
                key = meta.get('key', '').lower()
                if 'routeapp_shipment_tracking_number' in key:
                    value = meta.get('value', '').strip()
                    if value and len(value) > 5:
                        tracking_number = value
                        logger.info(f"Found RouteApp tracking: {tracking_number}")
                        break
        
        response_data = {
            'success': True,
            'order_id': order.get('id'),
            'order_number': order.get('number'),
            'order_status': order_status,
            'order_date': order_date,
            'tracking_number': tracking_number,
            'carrier': tracking_provider.upper() if tracking_provider else None
        }
        
        # If we have a tracking number, use direct tracking URL
        if tracking_number:
            response_data['message'] = f"Order {order_status.lower()}: Tracking number {tracking_number}"
            response_data['tracking_url'] = get_tracking_url(tracking_number, tracking_provider)
            logger.info(f"Using direct tracking URL: {response_data['tracking_url']}")
        else:
            response_data['message'] = f"Order {order_status.lower()}: No tracking information available"
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error tracking order: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve tracking information. Please try again later.'
        }), 500

def get_tracking_url(tracking_number, provider):
    """
    Generate tracking URL based on provider
    """
    if not tracking_number:
        return None
        
    if not provider:
        return None  # Don't default to anything if provider is unknown
        
    provider = provider.lower()
    
    if provider == 'usps':
        return f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"
    elif provider == 'ups':
        return f"https://www.ups.com/track?loc=en_US&tracknum={tracking_number}"
    elif provider == 'fedex':
        return f"https://www.fedex.com/fedextrack/?trknbr={tracking_number}"
    elif provider == 'dhl':
        return f"https://www.dhl.com/us-en/home/tracking/tracking-express.html?submit=1&tracking-id={tracking_number}"
    else:
        return None  # Return None for unknown providers instead of defaulting

def get_woocommerce_order(order_number):
    """
    Get order details from WooCommerce
    """
    try:
        url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/orders"
        auth = (WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)
        
        # Search by order number
        params = {
            'search': order_number,
            'per_page': 50,
            'status': 'any'
        }
        
        response = requests.get(url, auth=auth, params=params, timeout=30)
        
        if response.status_code == 200:
            orders = response.json()
            
            # Find exact match by order number or ID
            for order in orders:
                if str(order.get('number', '')) == str(order_number) or str(order.get('id', '')) == str(order_number):
                    return order
        
        # Try direct ID lookup if order_number is numeric
        if order_number.isdigit():
            direct_url = f"{url}/{order_number}"
            response = requests.get(direct_url, auth=auth, timeout=30)
            if response.status_code == 200:
                return response.json()
        
        return None
        
    except Exception as e:
        logger.error(f"WooCommerce API error: {e}")
        return None

