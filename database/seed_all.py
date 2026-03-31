#!/usr/bin/env python3
"""
Comprehensive seed script for MindGuard database.

Populates all core tables with realistic Vietnamese fake data
so the application looks alive for demos and presentations.

Usage:
    cd database/
    python seed_all.py

Tables seeded:
    - registrations  (1 admin + 8 users)
    - scammer_reports (20 scammer entries)
    - scammer_leaderboard (1 entry per approved scammer)
    - scam_reports   (8 educational articles)
    - quiz_results   (15 quiz attempts)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import (
    Registration,
    ScammerReport,
    ScammerLeaderboard,
    ScamReport,
    QuizResult,
)
from werkzeug.security import generate_password_hash
from utils.encryption import encrypt_scammer_info, hash_reporter_id, serialize_evidence
from utils.helpers import calculate_danger_level
from config import Config
from datetime import datetime, timedelta
import random
import json
import string


# ---------------------------------------------------------------------------
# 1. Admin account
# ---------------------------------------------------------------------------

def seed_admin():
    """Create the default admin account if it does not exist."""
    print("\n[1/6] Seeding admin account ...")

    existing = Registration.query.filter_by(email="admin@mindguard.com").first()
    if existing:
        print("  -> Admin already exists, skipping.")
        return existing

    admin = Registration(
        name="Admin MindGuard",
        email="admin@mindguard.com",
        password_hash=generate_password_hash("mindguard2025"),
        role="admin",
        is_admin=True,
        date_of_birth="1990-01-15",
        occupation="Quan tri vien",
        city="Ha Noi",
        phone_number="0901000000",
        bio="Quan tri vien he thong MindGuard.",
        onboarding_completed=True,
    )
    db.session.add(admin)
    db.session.flush()
    print("  -> Admin created: admin@mindguard.com / mindguard2025")
    return admin


# ---------------------------------------------------------------------------
# 2. Regular users
# ---------------------------------------------------------------------------

USER_DATA = [
    {
        "name": "Nguyen Van An",
        "email": "nguyenvanan98@gmail.com",
        "dob": "1998-06-12",
        "occupation": "Sinh vien",
        "city": "Ha Noi",
        "phone": "0912345678",
        "bio": "Sinh vien nam cuoi DH Bach Khoa Ha Noi, quan tam den an ninh mang.",
    },
    {
        "name": "Tran Thi Bich Ngoc",
        "email": "bichngoc.tran@gmail.com",
        "dob": "1995-03-22",
        "occupation": "Nhan vien van phong",
        "city": "TP. Ho Chi Minh",
        "phone": "0387654321",
        "bio": "Lam viec tai cong ty TNHH Thanh Dat, hay mua sam online.",
    },
    {
        "name": "Le Hoang Minh",
        "email": "lhminh.dev@gmail.com",
        "dob": "1997-11-05",
        "occupation": "Lap trinh vien",
        "city": "Da Nang",
        "phone": "0856789012",
        "bio": "Full-stack developer, thich nghien cuu bao mat.",
    },
    {
        "name": "Pham Thi Huong",
        "email": "huongpham.teacher@gmail.com",
        "dob": "1988-08-15",
        "occupation": "Giao vien",
        "city": "Hai Phong",
        "phone": None,
        "bio": "Giao vien cap 3, muon day hoc sinh nhan biet lua dao.",
    },
    {
        "name": "Vo Duc Tai",
        "email": "ductai.vo@gmail.com",
        "dob": "1992-01-30",
        "occupation": "Kinh doanh online",
        "city": "Can Tho",
        "phone": "0976543210",
        "bio": None,
    },
    {
        "name": "Hoang Thi Mai Anh",
        "email": "maianh.hoang@gmail.com",
        "dob": "2000-12-01",
        "occupation": "Sinh vien",
        "city": "Hue",
        "phone": "0345678901",
        "bio": "Sinh vien DH Khoa hoc Hue, hay tham gia cac CLB tinh nguyen.",
    },
    {
        "name": "Bui Quang Huy",
        "email": "quanghuy.bui@gmail.com",
        "dob": "1985-07-20",
        "occupation": "Bac si",
        "city": "Ha Noi",
        "phone": None,
        "bio": "Bac si noi khoa, nhan thay nhieu benh nhan bi lua mat tien.",
    },
    {
        "name": "Dang Ngoc Linh",
        "email": "ngoclinh.dang@gmail.com",
        "dob": "1993-04-18",
        "occupation": "Ky su",
        "city": "TP. Ho Chi Minh",
        "phone": "0823456789",
        "bio": "Ky su xay dung, tung bi lua mua dat gia nen muon canh bao moi nguoi.",
    },
]


def seed_users():
    """Create regular user accounts. Returns list of created/existing users."""
    print("\n[2/6] Seeding user accounts ...")

    users = []
    for u in USER_DATA:
        existing = Registration.query.filter_by(email=u["email"]).first()
        if existing:
            print(f"  -> Exists, skipping: {u['email']}")
            users.append(existing)
            continue

        reg = Registration(
            name=u["name"],
            email=u["email"],
            password_hash=generate_password_hash("user123"),
            role="user",
            is_admin=False,
            date_of_birth=u["dob"],
            occupation=u["occupation"],
            city=u["city"],
            phone_number=u["phone"],
            bio=u["bio"],
            onboarding_completed=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(10, 120)),
        )
        db.session.add(reg)
        users.append(reg)
        print(f"  -> Created: {u['name']} ({u['email']})")

    db.session.flush()
    print(f"  Total users (excl. admin): {len(users)}")
    return users


# ---------------------------------------------------------------------------
# 3. Scammer reports
# ---------------------------------------------------------------------------

SCAMMER_DATA = [
    # --- Phone scams: gia danh cong an / vien kiem sat ---
    {
        "identifier": "0963551234",
        "name": "Gia danh Cong an Quan 1",
        "report_type": "phone",
        "bank_name": None,
        "scammer_email": None,
        "social_link": None,
        "scam_type": "Gia danh co quan chuc nang",
        "platform": "Dien thoai",
        "description": (
            "Tu xung la Thieu ta Cong an Quan 1 TP.HCM, thong bao so CMND cua toi "
            "lien quan den duong day rua tien. Yeu cau chuyen 50 trieu vao 'tai khoan "
            "tam giu' de phuc vu dieu tra, de doa bat giam neu khong hop tac."
        ),
        "evidence": ["https://imgur.com/fake-evidence-1.jpg"],
        "status": "approved",
        "verification": "verified",
        "report_count": 45,
        "confirmed": 22,
        "risk_score": 92,
    },
    {
        "identifier": "0335987654",
        "name": "Gia danh Vien Kiem Sat",
        "report_type": "phone",
        "bank_name": None,
        "scammer_email": None,
        "social_link": None,
        "scam_type": "Gia danh co quan chuc nang",
        "platform": "Dien thoai",
        "description": (
            "Goi dien tu so la, tu xung Vien kiem sat Nhan dan tinh Binh Duong. "
            "Noi rang toi co lenh bat tam giam vi co tai khoan ngan hang lien quan den "
            "vu an buon ban ma tuy. Yeu cau tai app la va cung cap OTP de 'xac minh'."
        ),
        "evidence": ["https://imgur.com/fake-evidence-2.jpg", "https://imgur.com/call-log-2.png"],
        "status": "approved",
        "verification": "verified",
        "report_count": 38,
        "confirmed": 18,
        "risk_score": 88,
    },
    # --- Bank account scams ---
    {
        "identifier": "1017654321",
        "name": "Nguyen Van Hung (gia)",
        "report_type": "bank",
        "bank_name": "Vietcombank",
        "scammer_email": None,
        "social_link": "https://facebook.com/profile-fake-01",
        "scam_type": "Lua dao chuyen khoan",
        "platform": "Facebook Marketplace",
        "description": (
            "Rao ban iPhone 15 Pro Max gia 12 trieu (gia thi truong 28 trieu). "
            "Yeu cau chuyen khoan dat coc 3 trieu vao STK Vietcombank. Sau khi "
            "nhan tien thi khoa Facebook va so dien thoai khong lien lac duoc."
        ),
        "evidence": ["https://imgur.com/chat-screenshot-3.jpg"],
        "status": "approved",
        "verification": "verified",
        "report_count": 28,
        "confirmed": 15,
        "risk_score": 85,
    },
    {
        "identifier": "9876543210",
        "name": "Tran Thi Loan (gia)",
        "report_type": "bank",
        "bank_name": "Techcombank",
        "scammer_email": None,
        "social_link": "https://zalo.me/fake-seller-04",
        "scam_type": "Lua dao ban hang online",
        "platform": "Zalo",
        "description": (
            "Ban my pham xach tay gia re tren Zalo, san pham la hang gia. "
            "Khi khach khieu nai thi chan so va khong hoan tien. Nhieu nan nhan "
            "bao cao cung mot so tai khoan Techcombank."
        ),
        "evidence": ["https://imgur.com/product-fake-4.jpg", "https://imgur.com/chat-zalo-4.png"],
        "status": "approved",
        "verification": "verified",
        "report_count": 22,
        "confirmed": 12,
        "risk_score": 78,
    },
    # --- Phishing ---
    {
        "identifier": "https://vietcombank-online.tk",
        "name": "Website gia mao Vietcombank",
        "report_type": "website",
        "bank_name": "Vietcombank",
        "scammer_email": "support@vietcombank-online.tk",
        "social_link": None,
        "scam_type": "Phishing",
        "platform": "SMS, Email",
        "description": (
            "Website gia mao giao dien VCB Digibank, gui link qua SMS brand name gia. "
            "Nan nhan dang nhap va nhap OTP, bi rut sach tien trong tai khoan. "
            "Domain dang ky o nuoc ngoai, khong phai website chinh thuc cua Vietcombank."
        ),
        "evidence": [
            "https://imgur.com/phishing-site-5.jpg",
            "https://imgur.com/sms-fake-5.png",
        ],
        "status": "approved",
        "verification": "verified",
        "report_count": 65,
        "confirmed": 30,
        "risk_score": 95,
    },
    {
        "identifier": "https://mbbank-verify.xyz",
        "name": "Website gia mao MB Bank",
        "report_type": "website",
        "bank_name": "MB Bank",
        "scammer_email": "verify@mbbank-verify.xyz",
        "social_link": None,
        "scam_type": "Phishing",
        "platform": "Email",
        "description": (
            "Gui email gia mao thong bao tai khoan bi khoa, yeu cau click link de "
            "xac minh. Trang web giong het app MB Bank, sau khi nhap tai khoan va mat "
            "khau thi bi chuyen het tien."
        ),
        "evidence": ["https://imgur.com/phishing-mb-6.jpg"],
        "status": "approved",
        "verification": "verified",
        "report_count": 33,
        "confirmed": 16,
        "risk_score": 90,
    },
    # --- Crypto / Forex investment scams ---
    {
        "identifier": "https://binance-vn-pro.com",
        "name": "San giao dich Binance gia",
        "report_type": "website",
        "bank_name": None,
        "scammer_email": "support@binance-vn-pro.com",
        "social_link": "https://t.me/binancevnpro",
        "scam_type": "Lua dao dau tu tien ao",
        "platform": "Telegram, Facebook",
        "description": (
            "Lap nhom Telegram moi tham gia dau tu Bitcoin voi loi nhuan 30%/thang. "
            "San giao dich gia mao Binance, cho rut lan dau de tao long tin. "
            "Khi nap so luong lon thi khoa tai khoan va bien mat."
        ),
        "evidence": [
            "https://imgur.com/crypto-scam-7a.jpg",
            "https://imgur.com/crypto-scam-7b.jpg",
        ],
        "status": "approved",
        "verification": "verified",
        "report_count": 52,
        "confirmed": 25,
        "risk_score": 93,
    },
    {
        "identifier": "0889123456",
        "name": "Forex Academy VN",
        "report_type": "phone",
        "bank_name": "VPBank",
        "scammer_email": "contact@forexacademyvn.com",
        "social_link": "https://facebook.com/forexacademyvn",
        "scam_type": "Lua dao dau tu Forex",
        "platform": "Facebook, Zalo",
        "description": (
            "Tu xung chuyen gia tai chinh, quang cao khoa hoc Forex mien phi. "
            "Sau do du do nap tien vao san MT5 gia, cam ket loi nhuan 50%/thang. "
            "Nhieu nan nhan mat tu 20-200 trieu dong."
        ),
        "evidence": ["https://imgur.com/forex-scam-8.jpg"],
        "status": "approved",
        "verification": "verified",
        "report_count": 18,
        "confirmed": 9,
        "risk_score": 75,
    },
    # --- Loan shark apps ---
    {
        "identifier": "VayNhanh360",
        "name": "App VayNhanh360",
        "report_type": "app",
        "bank_name": None,
        "scammer_email": None,
        "social_link": "https://vaynhanh360.vn",
        "scam_type": "Tin dung den - App vay nang lai",
        "platform": "Google Play (da bi go)",
        "description": (
            "App cho vay tien online voi lai suat cat co 730%/nam. Truy cap danh ba "
            "dien thoai, gui tin nhan de doa den nguoi than khi cham tra. "
            "Nhieu nan nhan bi quay roi va khung bo tinh than."
        ),
        "evidence": [
            "https://imgur.com/loan-shark-9a.jpg",
            "https://imgur.com/loan-shark-9b.jpg",
            "https://imgur.com/loan-shark-9c.jpg",
        ],
        "status": "approved",
        "verification": "verified",
        "report_count": 80,
        "confirmed": 28,
        "risk_score": 95,
    },
    {
        "identifier": "TienOi.vn",
        "name": "App TienOi",
        "report_type": "app",
        "bank_name": None,
        "scammer_email": None,
        "social_link": None,
        "scam_type": "Tin dung den - App vay nang lai",
        "platform": "Link APK (ngoai store)",
        "description": (
            "Yeu cau cai dat file APK tu link ngoai CH Play. Vay 3 trieu nhung thuc "
            "nhan 2.1 trieu sau khi tru phi. Lai suat tinh theo ngay, sau 1 thang no "
            "len 7 trieu. Goi dien khung bo va gui anh ghep cho ban be tren Facebook."
        ),
        "evidence": ["https://imgur.com/tienoi-10.jpg"],
        "status": "approved",
        "verification": "verified",
        "report_count": 41,
        "confirmed": 20,
        "risk_score": 91,
    },
    # --- Job scams ---
    {
        "identifier": "0376543210",
        "name": "Tuyen CTV Shopee gia",
        "report_type": "phone",
        "bank_name": "BIDV",
        "scammer_email": None,
        "social_link": "https://t.me/shopee_ctv_official",
        "scam_type": "Lua dao tuyen dung",
        "platform": "Telegram",
        "description": (
            "Tuyen cong tac vien chot don cho Shopee, moi nhiem vu duoc 20-50k. "
            "Lam vai nhiem vu dau duoc tra tien that. Sau do yeu cau nap tien de "
            "'mo khoa nhiem vu VIP', nap xong thi chan tai khoan."
        ),
        "evidence": [
            "https://imgur.com/job-scam-11a.jpg",
            "https://imgur.com/job-scam-11b.jpg",
        ],
        "status": "approved",
        "verification": "verified",
        "report_count": 35,
        "confirmed": 17,
        "risk_score": 87,
    },
    {
        "identifier": "0812345000",
        "name": "Viec nhe luong cao Facebook",
        "report_type": "phone",
        "bank_name": "VPBank",
        "scammer_email": None,
        "social_link": "https://facebook.com/vieclamtaigia2025",
        "scam_type": "Lua dao tuyen dung",
        "platform": "Facebook",
        "description": (
            "Dang tuyen nhan vien danh may tai nha luong 15-20 trieu/thang. "
            "Yeu cau dong phi 500k mua tai lieu va phan mem. Sau khi chuyen tien "
            "thi gui file rac va khong tra luong."
        ),
        "evidence": ["https://imgur.com/job-scam-12.jpg"],
        "status": "approved",
        "verification": "pending",
        "report_count": 12,
        "confirmed": 5,
        "risk_score": 65,
    },
    # --- Romance scams ---
    {
        "identifier": "0945678123",
        "name": "Lua tinh - Jack (gia My kieu)",
        "report_type": "phone",
        "bank_name": "Techcombank",
        "scammer_email": "jack.wilson.real@gmail.com",
        "social_link": "https://facebook.com/jack.wilson.fake.profile",
        "scam_type": "Lua dao tinh cam",
        "platform": "Facebook, Zalo",
        "description": (
            "Tu xung la Viet kieu My, lam doanh nhan. Lam quen qua Facebook, "
            "nhan tin ngot ngao 3 thang. Sau do nho chuyen 80 trieu dong "
            "phi hai quan de nhan 'qua tang tu My'. Sau khi chuyen tien thi mat lien lac."
        ),
        "evidence": [
            "https://imgur.com/romance-13a.jpg",
            "https://imgur.com/romance-13b.jpg",
        ],
        "status": "approved",
        "verification": "verified",
        "report_count": 15,
        "confirmed": 8,
        "risk_score": 72,
    },
    {
        "identifier": "0367891234",
        "name": "Lua tinh qua Tinder",
        "report_type": "phone",
        "bank_name": "MB Bank",
        "scammer_email": None,
        "social_link": "https://tinder.com/@fakesarah",
        "scam_type": "Lua dao tinh cam",
        "platform": "Tinder, Zalo",
        "description": (
            "Gap tren Tinder, hen ho 2 thang. Sau do ke chuyen bo me bi benh, "
            "muon vay 30 trieu se tra lai. Nhan duoc tien xong thi xoa tai khoan "
            "Tinder va chan so Zalo."
        ),
        "evidence": ["https://imgur.com/romance-14.jpg"],
        "status": "approved",
        "verification": "verified",
        "report_count": 8,
        "confirmed": 4,
        "risk_score": 55,
    },
    # --- Real estate scams ---
    {
        "identifier": "3456789012",
        "name": "Cong ty BDS Phu Thinh (gia)",
        "report_type": "bank",
        "bank_name": "BIDV",
        "scammer_email": "phuthinh.bds@gmail.com",
        "social_link": "https://facebook.com/phuthinhbds",
        "scam_type": "Lua dao bat dong san",
        "platform": "Facebook, Trang web",
        "description": (
            "Rao ban dat nen du an 'Khu do thi Phu Thinh' o Long An voi gia re. "
            "Thu tien dat coc 200-500 trieu nhung du an khong co that. "
            "Giay to phap ly gia mao, cong ty khong co giay phep kinh doanh BDS."
        ),
        "evidence": [
            "https://imgur.com/realestate-15a.jpg",
            "https://imgur.com/realestate-15b.jpg",
        ],
        "status": "approved",
        "verification": "verified",
        "report_count": 25,
        "confirmed": 14,
        "risk_score": 82,
    },
    # --- Lottery / prize scams ---
    {
        "identifier": "0901234567",
        "name": "Trung thuong Viettel gia",
        "report_type": "phone",
        "bank_name": "Agribank",
        "scammer_email": None,
        "social_link": None,
        "scam_type": "Lua dao trung thuong",
        "platform": "Dien thoai, SMS",
        "description": (
            "Goi dien/gui SMS thong bao trung giai dac biet chuong trinh Viettel "
            "tri gia 500 trieu. Yeu cau dong thue 10% (50 trieu) vao STK Agribank "
            "truoc khi nhan thuong. Viettel xac nhan khong co chuong trinh nay."
        ),
        "evidence": ["https://imgur.com/lottery-16.jpg"],
        "status": "approved",
        "verification": "verified",
        "report_count": 20,
        "confirmed": 10,
        "risk_score": 70,
    },
    # --- Facebook marketplace scams ---
    {
        "identifier": "5678901234",
        "name": "Ban Macbook lua dao",
        "report_type": "bank",
        "bank_name": "VPBank",
        "scammer_email": None,
        "social_link": "https://facebook.com/marketplace/fake-macbook",
        "scam_type": "Lua dao ban hang online",
        "platform": "Facebook Marketplace",
        "description": (
            "Rao ban Macbook Air M2 gia 8 trieu (gia thi truong 22 trieu). "
            "Gui hinh that nhung ship hang la hop rong. Tai khoan Facebook "
            "moi tao 1 thang, khong co ban be that."
        ),
        "evidence": ["https://imgur.com/marketplace-17.jpg"],
        "status": "pending",
        "verification": "pending",
        "report_count": 5,
        "confirmed": 2,
        "risk_score": 45,
    },
    # --- Pending / new reports ---
    {
        "identifier": "0398765432",
        "name": "Gia danh nhan vien Dien luc",
        "report_type": "phone",
        "bank_name": None,
        "scammer_email": None,
        "social_link": None,
        "scam_type": "Gia danh co quan chuc nang",
        "platform": "Dien thoai",
        "description": (
            "Goi dien tu xung la nhan vien Dien luc, noi hoa don thang nay "
            "tang dot bien va se bi cat dien trong 2 gio neu khong thanh toan "
            "ngay. Yeu cau chuyen tien qua ma QR."
        ),
        "evidence": [],
        "status": "pending",
        "verification": "unverified",
        "report_count": 3,
        "confirmed": 0,
        "risk_score": 25,
    },
    # --- Rejected report (false positive) ---
    {
        "identifier": "0321654987",
        "name": "Bao cao sai - Shop chinh hang",
        "report_type": "phone",
        "bank_name": None,
        "scammer_email": None,
        "social_link": "https://shopee.vn/shop-chinh-hang",
        "scam_type": "Lua dao ban hang online",
        "platform": "Shopee",
        "description": (
            "Bao cao la shop lua dao nhung sau xac minh day la shop chinh hang "
            "co giay phep kinh doanh hop le. Nguoi bao cao hieu nham vi giao "
            "hang cham do van chuyen."
        ),
        "evidence": [],
        "status": "rejected",
        "verification": "unverified",
        "report_count": 1,
        "confirmed": 0,
        "risk_score": 10,
    },
    # --- Gia mao ngan hang qua SMS ---
    {
        "identifier": "0899876543",
        "name": "SMS gia mao BIDV",
        "report_type": "phone",
        "bank_name": "BIDV",
        "scammer_email": None,
        "social_link": None,
        "scam_type": "Phishing",
        "platform": "SMS Brandname",
        "description": (
            "Gui SMS Brandname gia mao BIDV thong bao tai khoan bi tam khoa. "
            "Link dan den trang web gia mao BIDV SmartBanking. Nhieu nguoi mat "
            "tien vi nhap mat khau va OTP vao trang gia."
        ),
        "evidence": ["https://imgur.com/sms-bidv-20.jpg", "https://imgur.com/fake-bidv-site-20.jpg"],
        "status": "approved",
        "verification": "verified",
        "report_count": 55,
        "confirmed": 24,
        "risk_score": 94,
    },
]


def seed_scammers():
    """Create scammer report entries. Returns list of created ScammerReport objects."""
    print("\n[3/6] Seeding scammer reports ...")

    reports = []
    reporter_names = [
        "anonymous_reporter_01",
        "reporter_hanoi_02",
        "reporter_hcm_03",
        "reporter_danang_04",
        "nguoitocao_05",
        "nannhan_06",
        "canhbao_07",
        "baocao_08",
    ]

    for idx, s in enumerate(SCAMMER_DATA):
        # Use raw identifier to check for duplicates
        existing = ScammerReport.query.filter_by(scammer_info_raw=s["identifier"]).first()
        if existing:
            print(f"  -> Exists, skipping: {s['name']}")
            reports.append(existing)
            continue

        days_ago = random.randint(1, 90)
        created = datetime.utcnow() - timedelta(days=days_ago)
        updated = created + timedelta(days=random.randint(0, min(days_ago, 15)))

        reporter_key = random.choice(reporter_names) + f"_{idx}"

        evidence_json = serialize_evidence(s["evidence"]) if s["evidence"] else "[]"

        report = ScammerReport(
            scammer_identifier=encrypt_scammer_info(
                s["identifier"], Config.REPORT_ENCRYPTION_KEY
            ),
            scammer_info_raw=s["identifier"],
            scammer_name=s["name"],
            report_type=s["report_type"],
            bank_name=s["bank_name"],
            scammer_email=s["scammer_email"],
            social_link=s["social_link"],
            scam_type=s["scam_type"],
            platform=s["platform"],
            description=s["description"],
            evidence_urls=evidence_json,
            reporter_hash=hash_reporter_id(reporter_key),
            status=s["status"],
            verification_status=s["verification"],
            risk_score=s["risk_score"],
            confirmed_by_count=s["confirmed"],
            report_count=s["report_count"],
            created_at=created,
            updated_at=updated,
        )
        db.session.add(report)
        reports.append(report)
        print(f"  -> Created: {s['name']} ({s['scam_type']}) [risk={s['risk_score']}]")

    db.session.flush()
    print(f"  Total scammer reports: {len(reports)}")
    return reports


# ---------------------------------------------------------------------------
# 4. Scammer leaderboard
# ---------------------------------------------------------------------------

def seed_leaderboard(scammer_reports):
    """Create leaderboard entries for all approved scammer reports."""
    print("\n[4/6] Seeding scammer leaderboard ...")

    count = 0
    for report in scammer_reports:
        # Only approved scammers go on the leaderboard
        if report.status != "approved":
            continue

        existing = ScammerLeaderboard.query.filter_by(scammer_id=report.id).first()
        if existing:
            print(f"  -> Exists, skipping leaderboard for scammer_id={report.id}")
            continue

        danger = calculate_danger_level(report.report_count)

        entry = ScammerLeaderboard(
            scammer_id=report.id,
            total_reports=report.report_count,
            danger_level=danger,
            last_reported=report.updated_at or report.created_at,
        )
        db.session.add(entry)
        count += 1
        print(
            f"  -> Leaderboard: {report.scammer_name} "
            f"(reports={report.report_count}, danger={danger})"
        )

    db.session.flush()
    print(f"  Total leaderboard entries: {count}")


# ---------------------------------------------------------------------------
# 5. Educational articles (ScamReport / knowledge base)
# ---------------------------------------------------------------------------

ARTICLE_DATA = [
    {
        "title": "Nhan dien lua dao 'Tuyen dung viec nhe luong cao'",
        "category": "Tuyen dung",
        "channel": "Telegram, Zalo",
        "description": (
            "Cac doi tuong thuong dang bai tuyen cong tac vien chot don, like dao, "
            "xem video TikTok kiem tien. Yeu cau nap tien de lam nhiem vu hoac "
            "nang cap tai khoan VIP. Nhieu nan nhan mat tu 5-100 trieu dong."
        ),
        "tip": (
            "Khong bao gio nap tien de duoc lam viec. Cac cong ty chan chinh "
            "khong yeu cau dat coc. Kiem tra ma so thue va dia chi cong ty "
            "tren Cong thong tin Dang ky Doanh nghiep."
        ),
    },
    {
        "title": "Canh bao thu doan gia danh cong an, vien kiem sat",
        "category": "Gia danh",
        "channel": "Dien thoai (VoIP)",
        "description": (
            "Goi dien thong bao ban co lien quan den vu an ma tuy, rua tien. "
            "Yeu cau chuyen tien vao 'tai khoan tam giu' de phuc vu dieu tra "
            "hoac cai ung dung la de lay cap OTP. Muc tieu chinh la nguoi lon tuoi."
        ),
        "tip": (
            "Co quan cong an KHONG lam viec qua dien thoai. KHONG chuyen tien, "
            "KHONG cai app qua link la (.apk). Goi 113 de xac minh."
        ),
    },
    {
        "title": "Lua dao tinh cam (Romance Scam) - Cach nhan biet",
        "category": "Tinh cam",
        "channel": "Tinder, Facebook Dating",
        "description": (
            "Ke lua ket ban, tan tinh qua mang trong thoi gian dai (2-6 thang). "
            "Sau do nho nhan ho qua tu nuoc ngoai (phai dong thue hai quan) "
            "hoac ru re dau tu tien ao lai suat cao."
        ),
        "tip": (
            "Canh giac voi nguoi yeu tren mang chua tung gap mat nhung doi tien. "
            "Khong nhan qua, khong chuyen khoan cho 'nhan vien hai quan' gia mao. "
            "Kiem tra anh bang Google Reverse Image Search."
        ),
    },
    {
        "title": "Gia mao nhan vien ngan hang nang han muc the tin dung",
        "category": "Tai chinh",
        "channel": "SMS Brandname Fake, Zalo",
        "description": (
            "Gui tin nhan SMS co ten thuong hieu (Brandname) gia mao, chua link "
            "lua dao yeu cau dang nhap va cung cap OTP de nang han muc hoac "
            "huy phi thuong nien. Thiet ke web giong het ngan hang that."
        ),
        "tip": (
            "Khong click vao link trong tin nhan SMS. Goi truc tiep len tong dai "
            "ngan hang (ghi tren the) de xac minh. Kiem tra URL co dung domain "
            "chinh thuc khong."
        ),
    },
    {
        "title": "Tin dung den - App vay nang lai va cach phong tranh",
        "category": "Tin dung den",
        "channel": "Google Play, link APK",
        "description": (
            "App cho vay tien voi lai suat cat co 500-1000%/nam. Truy cap danh ba, "
            "anh, tin nhan tren dien thoai. Khi cham tra, gui tin nhan de doa den "
            "nguoi than, ghep anh khieu dam de tong tien."
        ),
        "tip": (
            "Chi vay tien o to chuc tai chinh duoc Bo Tai chinh cap phep. "
            "Kiem tra thong tin tren Ngan hang Nha nuoc. Khong cai app tu link "
            "ngoai CH Play/App Store. Bao cong an neu bi de doa."
        ),
    },
    {
        "title": "Lua dao dau tu tien ao, san Forex gia mao",
        "category": "Dau tu",
        "channel": "Telegram, Facebook, Zalo",
        "description": (
            "Lap nhom kin moi dau tu Bitcoin, Forex voi loi nhuan 20-50%/thang. "
            "San giao dich gia mao, cho rut tien lan dau de tao long tin. "
            "Khi nap so luong lon thi khoa tai khoan va bien mat."
        ),
        "tip": (
            "Khong co hinh thuc dau tu nao dam bao loi nhuan co dinh 20-50%/thang. "
            "Chi giao dich tren san duoc Uy ban Chung khoan cap phep. "
            "Canh giac voi loi moi dau tu tu nguoi la tren mang xa hoi."
        ),
    },
    {
        "title": "Phishing - Cach nhan biet website gia mao ngan hang",
        "category": "Phishing",
        "channel": "SMS, Email",
        "description": (
            "Website phishing sao chep giao dien Internet Banking cua cac ngan hang "
            "lon (Vietcombank, BIDV, MB Bank...). Nan nhan nhap ten dang nhap, mat "
            "khau va OTP, bi ke gian rut tien ngay lap tuc."
        ),
        "tip": (
            "Luon kiem tra URL tren thanh dia chi: ngan hang chinh thuc su dung "
            "domain .com.vn hoac .vn. Su dung app chinh thuc thay vi truy cap web. "
            "Bat 2FA va dat han muc chuyen tien thap."
        ),
    },
    {
        "title": "Lua dao trung thuong, qua tang gia - Chieu tro cu nhung van hieu qua",
        "category": "Trung thuong",
        "channel": "Dien thoai, SMS, Facebook",
        "description": (
            "Thong bao trung thuong xe may, dien thoai, tien mat tu cac chuong trinh "
            "khong co that (Viettel, Vingroup, Lazada...). Yeu cau dong phi/thue "
            "truoc khi nhan thuong. So tien 'phi' tu 500k den 50 trieu."
        ),
        "tip": (
            "Khong co chuong trinh trung thuong nao yeu cau tra tien truoc. "
            "Kiem tra thong tin tren website chinh thuc cua thuong hieu. "
            "Bao cho nguoi than, dac biet la nguoi lon tuoi."
        ),
    },
]


def seed_articles():
    """Create educational scam-awareness articles."""
    print("\n[5/6] Seeding educational articles ...")

    count = 0
    for art in ARTICLE_DATA:
        existing = ScamReport.query.filter_by(title=art["title"]).first()
        if existing:
            print(f"  -> Exists, skipping: {art['title'][:50]}...")
            continue

        article = ScamReport(
            title=art["title"],
            category=art["category"],
            channel=art["channel"],
            description=art["description"],
            protection_tip=art["tip"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(5, 60)),
        )
        db.session.add(article)
        count += 1
        print(f"  -> Created: {art['title'][:60]}...")

    db.session.flush()
    print(f"  Total articles: {count}")


# ---------------------------------------------------------------------------
# 6. Quiz results
# ---------------------------------------------------------------------------

def seed_quiz_results():
    """Create quiz result entries linked to seeded users."""
    print("\n[6/6] Seeding quiz results ...")

    users = Registration.query.filter(Registration.role == "user").all()
    if not users:
        print("  -> No users found, skipping quiz results.")
        return

    existing_count = QuizResult.query.count()
    if existing_count >= 15:
        print(f"  -> Already have {existing_count} quiz results, skipping.")
        return

    max_score = 15
    results_to_create = 15 - existing_count

    created = 0
    for i in range(results_to_create):
        user = random.choice(users)
        score = random.choice([5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

        # Generate certificate code for passing scores (>= 75%)
        cert_code = None
        if score >= 12:
            rand_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            cert_code = f"MG-{rand_part}"

        result = QuizResult(
            name=user.name,
            email=user.email,
            score=score,
            max_score=max_score,
            certificate_code=cert_code,
            created_at=datetime.utcnow() - timedelta(
                days=random.randint(1, 60),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            ),
        )
        db.session.add(result)
        created += 1

        pct = round(score / max_score * 100)
        cert_text = f", cert={cert_code}" if cert_code else ""
        print(f"  -> Quiz: {user.name} scored {score}/{max_score} ({pct}%){cert_text}")

    db.session.flush()
    print(f"  Total quiz results created: {created}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    with app.app_context():
        print("=" * 55)
        print("  MindGuard Database Seeder")
        print("  Populating all tables with realistic Vietnamese data")
        print("=" * 55)

        admin = seed_admin()
        db.session.commit()

        users = seed_users()
        db.session.commit()

        reports = seed_scammers()
        db.session.commit()

        seed_leaderboard(reports)
        db.session.commit()

        seed_articles()
        db.session.commit()

        seed_quiz_results()
        db.session.commit()

        # Summary
        print("\n" + "=" * 55)
        print("  SEED COMPLETE - Summary")
        print("=" * 55)
        print(f"  Registrations : {Registration.query.count()}")
        print(f"  Scammer Reports: {ScammerReport.query.count()}")
        print(f"  Leaderboard   : {ScammerLeaderboard.query.count()}")
        print(f"  Articles (KB) : {ScamReport.query.count()}")
        print(f"  Quiz Results  : {QuizResult.query.count()}")
        print("=" * 55)
        print("\n  Admin login: admin@mindguard.com / mindguard2025")
        print("  User login:  any seeded email  / user123")
        print()


if __name__ == "__main__":
    main()
