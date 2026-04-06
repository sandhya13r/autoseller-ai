# simulations/fake_chat.py
from utils.logger import log
from agent import memory
from agent.state_manager import transition
from services.buyer_service import extract_offer
from constants import AgentState

# ──────────────────────────────────────────
# SCRIPTED REPLY ENGINE
# ──────────────────────────────────────────
def get_scripted_reply(item_id: str, buyer_message: str) -> dict:
    log("fake_chat", f"🎬 Generating scripted reply for: {buyer_message[:40]}")

    msg_lower = buyer_message.lower().strip()

    # ── 1. check for price offer FIRST (highest priority)
    offer = extract_offer(buyer_message)
    if offer:
        mem          = memory.get(item_id)
        asking_price = mem.get("asking_price") or 55902
        min_price    = mem.get("min_price") or 52000
        rounds       = mem.get("counter_rounds") or 0

        if offer < min_price:
            memory.set(item_id, "counter_rounds", rounds + 1)
            return {
                "message": (
                    f"I appreciate the offer! Unfortunately "
                    f"₹{int(offer):,} is a bit too low for this one.\n\n"
                    f"Given the condition and all original accessories, "
                    f"the best I can do is ₹52000. "
                    f"That's already a great deal! What do you say? 😊"
                ),
                "type":          "counter",
                "counter_price": 52000
            }
        elif offer >= 52000:
            memory.set(item_id, "final_price", offer)
            transition(item_id, AgentState.DEAL_CONFIRMED)
            return {
                "message": (
                    f"🎉 Deal confirmed at ₹{int(offer):,}!\n\n"
                    f"I'm sending you a secure payment link now. "
                    f"Once payment is done, we'll schedule the pickup. "
                    f"Thank you for buying! 😊"
                ),
                "type":        "deal_confirmed",
                "final_price": offer
            }
        else:
            memory.set(item_id, "counter_rounds", rounds + 1)
            return {
                "message": (
                    f"You're close! I can do ₹52,000 as the final price. "
                    f"That's a fair deal with all accessories included. "
                    f"Shall we close at ₹52,000? 🤝"
                ),
                "type":          "counter",
                "counter_price": 52000
            }

    # ── 2. deal acceptance keywords
    deal_words = ["deal", "agreed", "accept", "confirmed", "let's do it",
                  "lets do it", "ok deal", "okay deal", "done", "finalise",
                  "finalize", "50000", "45000"]
    if any(w in msg_lower for w in deal_words):
        mem         = memory.get(item_id)
        final_price = mem.get("final_price") or 52000
        memory.set(item_id, "final_price", final_price)
        transition(item_id, AgentState.DEAL_CONFIRMED)
        return {
            "message": (
                f"🎉 Wonderful! Deal confirmed at ₹{int(final_price):,}!\n\n"
                f"Here's what happens next:\n"
                f"1. Complete the secure payment below\n"
                f"2. Seller will be notified immediately\n"
                f"3. Pickup will be scheduled within 24 hours\n\n"
                f"Sending payment link now... 💳"
            ),
            "type":        "deal_confirmed",
            "final_price": final_price
        }

    # ── 3. payment intent keywords
    pay_words = ["pay", "payment", "send", "send link", "send payment",
                 "upi", "gpay", "phonepe", "paytm", "how to pay",
                 "razorpay", "link", "pay now"]
    if any(w in msg_lower for w in pay_words):
        mem         = memory.get(item_id)
        final_price = mem.get("final_price")
        if final_price:
            # deal already confirmed, send payment
            return {
                "message": (
                    f"Here's your secure payment link for ₹{int(final_price):,}! 🔒\n\n"
                    f"Click the **Pay Now** button below to complete your purchase via Razorpay.\n"
                    f"Supports UPI, Cards, and Net Banking. ✅"
                ),
                "type": "send_payment_link"
            }
        else:
            return {
                "message": (
                    "Payment is 100% secure via Razorpay! 🔒\n\n"
                    "You can pay using:\n"
                    "💳 Credit/Debit Card\n"
                    "📱 UPI (GPay, PhonePe, Paytm)\n"
                    "🏦 Net Banking\n\n"
                    "First, shall we agree on a price? The asking price is ₹50,000. "
                    "Would you like to make an offer?"
                ),
                "type": "conversation"
            }

    # ── 4. availability / greeting keywords
    greet_words = ["available", "still", "hi", "hello", "hey", "hii",
                   "good morning", "good evening", "interested"]
    if any(w in msg_lower for w in greet_words):
        return {
            "message": (
                "Hi! 👋 Yes, the iPhone 13 is still available!\n\n"
                "📦 128GB | Good Condition | Battery 89%\n"
                "💰 Asking: ₹55,902\n\n"
                "Would you like to know more about the condition "
                "or make an offer?"
            ),
            "type": "conversation"
        }

    # ── 5. condition / quality questions
    condition_words = ["condition", "scratch", "damage", "screen", "battery",
                       "working", "problem", "issue", "crack", "repair",
                       "used", "how old", "age", "wear"]
    if any(w in msg_lower for w in condition_words):
        return {
            "message": (
                "Great question! Here's the honest condition report:\n\n"
                "✅ Screen — Perfect, no scratches\n"
                "⚠️ Back panel — Minor scratch (barely visible)\n"
                "✅ Battery health — 89%\n"
                "✅ Face ID — Working perfectly\n"
                "✅ All buttons — Fully functional\n\n"
                "Overall it's in great shape for daily use! "
                "Interested in making an offer?"
            ),
            "type": "conversation"
        }

    # ── 6. accessories / box questions
    accessory_words = ["box", "accessories", "charger", "cable", "earphone",
                       "original", "warranty", "bill", "invoice", "receipt"]
    if any(w in msg_lower for w in accessory_words):
        return {
            "message": (
                "Yes! Everything is included:\n\n"
                "📦 Original box\n"
                "🔌 Original charging cable\n"
                "📄 Original documentation\n\n"
                "No earphones (Apple stopped including them) "
                "but everything else is original. "
                "Want to make an offer?"
            ),
            "type": "conversation"
        }

    # ── 7. price / offer intent (no number given yet)
    price_intent_words = ["offer", "negotiate", "discount", "price",
                          "best price", "lowest", "how much", "rate",
                          "cost", "worth", "cheap", "deal", "bargain",
                          "make offer", "would like to", "want to buy",
                          "interested in buying"]
    if any(w in msg_lower for w in price_intent_words):
        return {
            "message": (
                "I'd love to hear your offer! 😊\n\n"
                "The asking price is ₹55,902 for this iPhone 13 "
                "in good condition with all accessories.\n\n"
                "What price are you thinking? Go ahead and name your number!"
            ),
            "type": "conversation"
        }

    # ── 8. affirmative short responses — ask them to name a price
    yes_words = ["yes", "yea", "yeah", "yep", "sure", "ok", "okay",
                 "alright", "fine", "of course", "definitely", "absolutely"]
    if any(w == msg_lower or msg_lower.startswith(w) for w in yes_words):
        mem         = memory.get(item_id)
        chat_history = memory.get_chat_history(item_id)
        last_agent   = None
        for m in reversed(chat_history[:-1]):  # skip current message
            if m["role"] == "agent":
                last_agent = m["message"]
                break

        # if last agent message was about payment, send payment link
        if last_agent and ("payment link" in last_agent.lower() or
                           "pay now" in last_agent.lower()):
            final_price = mem.get("final_price") or 48000
            return {
                "message": (
                    f"Here's your secure payment link for ₹{int(final_price):,}! 🔒\n\n"
                    f"Click the **Pay Now** button below to complete your purchase."
                ),
                "type": "send_payment_link"
            }

        # if deal was already confirmed
        if mem.get("final_price"):
            final_price = mem.get("final_price")
            return {
                "message": (
                    f"Great! Sending you the payment link for "
                    f"₹{int(final_price):,} now. 💳\n\n"
                    f"Click Pay Now below to complete securely via Razorpay."
                ),
                "type": "send_payment_link"
            }

        # otherwise guide them to make an offer
        return {
            "message": (
                "Awesome! The asking price is ₹55,902.\n\n"
                "Feel free to make an offer — just type the amount "
                "you have in mind and I'll check with the seller! 😊"
            ),
            "type": "conversation"
        }

    # ── 9. default fallback — guide toward offer
    return {
        "message": (
            "I'm here to help! 😊\n\n"
            "The iPhone 13 is available at ₹46,200 in good condition "
            "with all original accessories.\n\n"
            "You can:\n"
            "• Ask about the condition\n"
            "• Make a price offer\n"
            "• Ask about payment options\n\n"
            "What would you like to do?"
        ),
        "type": "conversation"
    }


# ──────────────────────────────────────────
# AUTO BUYER MESSAGES FOR DEMO
# ──────────────────────────────────────────
DEMO_BUYER_MESSAGES = [
    "Hi! Is this still available?",
    "What is the exact condition? Any scratches?",
    "Can you do ₹38,000?",
    "Okay how about ₹43,000?",
    "Deal! Let's proceed with ₹43,000"
]

def get_next_buyer_message(step: int) -> str:
    if step < len(DEMO_BUYER_MESSAGES):
        return DEMO_BUYER_MESSAGES[step]
    return ""