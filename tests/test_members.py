"""Unit tests for Member Model and MemberService."""

import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.schema import init_db
from database.repositories import MemberRepository
from models.member import Member
from models.person import Person
from services.member_service import MemberService


class TestMembers:
    """Test Member entity, inheritance, and MemberService operations."""

    @pytest.fixture
    def member_service(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = f.name
        init_db(temp_path, seed_samples=False)
        repo = MemberRepository(temp_path)
        service = MemberService(repo)
        yield service
        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass

    def test_member_inheritance_and_polymorphism(self):
        m = Member("MEM-10", "Devika Das", "devika@college.edu", "9876543210")
        
        # Module I: Inheritance
        assert isinstance(m, Person)
        assert isinstance(m, Member)
        
        # Module I: Polymorphism
        assert "Member" in m.get_role_display()
        assert "BORROW_BOOK" in m.get_permissions()

        # Encapsulation test
        with pytest.raises(ValueError):
            m.email = "not-an-email"

    def test_member_registration_and_search(self, member_service):
        member = member_service.register_member(
            member_id="MEM-TEST-1",
            name="Rahul Roy",
            email="rahul.roy@college.edu",
            phone="9876543210"
        )
        assert member.member_id == "MEM-TEST-1"

        # Duplicate ID should raise ValueError
        with pytest.raises(ValueError):
            member_service.register_member(
                member_id="MEM-TEST-1",
                name="Another Rahul",
                email="another@college.edu",
                phone="9876543211"
            )

        # Search
        results = member_service.search_members("Rahul")
        assert len(results) == 1
        assert results[0].member_id == "MEM-TEST-1"

    def test_member_delete_safeguard(self, member_service):
        member_service.register_member("MEM-SAFE", "Safe Member", "safe@college.edu", "9876543210")
        assert member_service.delete_member("MEM-SAFE") is True
        assert member_service.get_member("MEM-SAFE") is None
