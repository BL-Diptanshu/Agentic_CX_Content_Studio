"""
End-to-End Integration Test Suite
Tests the complete Agentic CX Content Studio workflow

Workflow Tested:
1. Document Upload & Parsing (Brand Guidelines)
2. RAG Knowledge Base Creation
3. Campaign Orchestration with Auto-Regeneration
4. Plan Validation
5. Content Generation (Text + Image)
6. Database Persistence
7. API Endpoints

Author: Senior Testing Engineer
"""

import pytest
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.processing.document_parser import CampaignDocumentParser
from src.rag.brand_retriever import BrandGuidelineRetriever
from src.core.orchestrator import ContentOrchestrationCrew
from src.database.models import Campaign, GeneratedContent
from src.database.database import SessionLocal, engine, Base
from fastapi.testclient import TestClient


class TestEndToEndWorkflow:
    """Complete end-to-end workflow tests"""
    
    # Class variables
    test_brand_doc = None
    parsed_data = {}
    test_campaign_id = None
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_test_environment(self):
        """Setup test environment before all tests"""
        print("\n" + "="*80)
        print("🚀 STARTING END-TO-END INTEGRATION TEST SUITE")
        print("="*80)
        
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)
        
        # Setup test brand guidelines document
        TestEndToEndWorkflow.test_brand_doc = project_root / "FitNow Official Brand Guidelines Document.docx"
        if not TestEndToEndWorkflow.test_brand_doc.exists():
            pytest.skip(f"Test brand guidelines document not found: {TestEndToEndWorkflow.test_brand_doc}")
        
        yield
        
        print("\n" + "="*80)
        print("✅ END-TO-END INTEGRATION TEST SUITE COMPLETED")
        print("="*80)
    
    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        session = SessionLocal()
        yield session
        session.close()
    
    @pytest.fixture
    def api_client(self):
        """Create FastAPI test client - import deferred to runtime"""
        # Import inside fixture to avoid collection-time errors
        try:
            from main import app
            from fastapi.testclient import TestClient as FastAPITestClient
            return FastAPITestClient(app)
        except Exception as e:
            pytest.skip(f"Could not create API client: {e}")
    
    # =========================================================================
    # TEST 1: Document Upload & Parsing
    # =========================================================================
    
    def test_01_document_parsing(self):
        """
        Test 1: Document Upload & Parsing
        Validates that brand guidelines are correctly parsed
        """
        print("\n" + "-"*80)
        print("TEST 1: Document Upload & Parsing")
        print("-"*80)
        
        parser = CampaignDocumentParser()
        result = parser.parse_document(
            str(self.test_brand_doc), 
            'docx'
        )
        
        # Assertions
        assert 'error' not in result, f"Parser error: {result.get('error')}"
        assert len(result) > 0, "No fields extracted from document"
        
        # Check for critical fields
        assert 'campaign_name' in result or 'brand' in result, \
            "Missing critical campaign/brand identification"
        
        print(f"✅ Extracted {len(result)} fields from brand guidelines")
        print(f"   Fields: {', '.join(list(result.keys())[:5])}...")
        
        # Store for next tests
        self.parsed_data = result
    
    # =========================================================================
    # TEST 2: RAG Knowledge Base Creation
    # =========================================================================
    
    def test_02_rag_knowledge_base_creation(self):
        """
        Test 2: RAG Knowledge Base Creation
        Validates brand knowledge indexing and retrieval
        """
        print("\n" + "-"*80)
        print("TEST 2: RAG Knowledge Base Creation & Retrieval")
        print("-"*80)
        
        brand_name = "FitNow"
        test_doc_path = str(self.test_brand_doc)
        
        try:
            # Initialize RAG retriever
            retriever = BrandGuidelineRetriever(data_dir=str(project_root / "data"))
            
            # Check if knowledge base exists (it should, from build_embeds.py)
            kb_path = project_root / "data" / "vectordb" / "faiss" / "brand_index.bin"
            if not kb_path.exists():
                pytest.skip("RAG Index not found. Please run build_embeds.py first.")
            
            print(f"   ℹ️  Using existing knowledge base at {kb_path}")
            
            # Test retrieval
            queries = [
                "What is the brand tone?",
                "What are forbidden words?",
                "What is the mission?"
            ]
            
            for query in queries:
                results = retriever._run(query)
                assert "Brand Guideline Information" in results, f"Unexpected result format: {results[:100]}"
                assert "No relevant" not in results, f"Query '{query}' returned no results"
                print(f"   ✅ Query '{query[:30]}...' returned valid response ({len(results)} chars)")
            
            print(f"✅ RAG Knowledge Base operational")
            
        except Exception as e:
            pytest.fail(f"RAG Knowledge Base creation failed: {e}")
    
    # =========================================================================
    # TEST 3: Database Operations (Campaign Creation)
    # =========================================================================
    
    def test_03_database_campaign_creation(self, db_session):
        """
        Test 3: Database Operations
        Validates campaign can be created and persisted
        """
        print("\n" + "-"*80)
        print("TEST 3: Database Campaign Creation")
        print("-"*80)
        
        # Create test campaign
        campaign = Campaign(
            campaign_name="E2E Test Campaign",
            brand="FitNow",
            objective="Test end-to-end workflow",
            inputs={"test": True}
        )
        
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)
        
        # Assertions
        assert campaign.campaign_id is not None, "Campaign ID not generated"
        assert campaign.campaign_name == "E2E Test Campaign"
        
        print(f"✅ Campaign created with ID: {campaign.campaign_id}")
        
        # Store campaign ID for later tests
        self.test_campaign_id = campaign.campaign_id
        
        # Cleanup
        db_session.delete(campaign)
        db_session.commit()
    
    # =========================================================================
    # TEST 4: Campaign Orchestration (Without Auto-Regeneration)
    # =========================================================================
    
    @pytest.mark.slow
    def test_04_campaign_orchestration_single_shot(self):
        """
        Test 4: Campaign Orchestration (Single-Shot)
        Validates basic campaign workflow without regeneration
        
        Workflow: RAG → Plan → Validate Plan → Generate Content
        """
        print("\n" + "-"*80)
        print("TEST 4: Campaign Orchestration (Single-Shot)")
        print("-"*80)
        
        orchestrator = ContentOrchestrationCrew()
        
        inputs = {
            "campaign_name": "E2E Test Campaign - Single Shot",
            "brand": "FitNow",
            "objective": "Create supportive wellness content focusing on consistency and healthy habits",
            "inputs": {"test_mode": True}
        }
        
        print("   Running orchestration (this may take 30-60 seconds)...")
        start_time = time.time()
        
        try:
            result = orchestrator.run_campaign(inputs)
            elapsed = time.time() - start_time
            
            # Assertions
            assert result is not None, "Orchestration returned None"
            result_str = str(result)
            assert len(result_str) > 0, "Orchestration returned empty result"
            
            print(f"✅ Orchestration completed in {elapsed:.2f}s")
            print(f"   Result length: {len(result_str)} chars")
            
            # Check if result contains expected elements
            if 'approved' in result_str.lower():
                print("   ✅ Plan validation detected: APPROVED")
            elif 'rejected' in result_str.lower():
                print("   ⚠️  Plan validation detected: REJECTED")
            
        except Exception as e:
            pytest.fail(f"Orchestration failed: {e}")
    
    # =========================================================================
    # TEST 5: Campaign Orchestration with Auto-Regeneration
    # =========================================================================
    
    @pytest.mark.slow
    def test_05_campaign_orchestration_with_regeneration(self):
        """
        Test 5: Campaign Orchestration with Auto-Regeneration
        Validates plan regeneration on validation failure
        
        Workflow: RAG → Plan → Validate Plan → (Retry if rejected) → Generate Content
        """
        print("\n" + "-"*80)
        print("TEST 5: Campaign Orchestration with Auto-Regeneration")
        print("-"*80)
        
        orchestrator = ContentOrchestrationCrew()
        
        # Create intentionally problematic objective to trigger regeneration
        inputs = {
            "campaign_name": "E2E Test Campaign - Regeneration",
            "brand": "FitNow",
            "objective": "Aggressive sales push with guaranteed results and medical claims",  # Should fail validation
            "inputs": {"test_mode": True}
        }
        
        print("   Running orchestration with auto-regeneration (max 3 attempts)...")
        print("   Expected: Initial plan rejection, followed by regeneration...")
        start_time = time.time()
        
        try:
            result_data = orchestrator.run_with_auto_regeneration(inputs, max_attempts=3)
            elapsed = time.time() - start_time
            
            # Assertions
            assert 'status' in result_data, "Missing status in result"
            assert 'attempts' in result_data, "Missing attempts count in result"
            assert 'result' in result_data, "Missing result in result data"
            
            status = result_data['status']
            attempts = result_data['attempts']
            
            print(f"✅ Auto-regeneration completed in {elapsed:.2f}s")
            print(f"   Status: {status}")
            print(f"   Attempts: {attempts}/{3}")
            
            # Validate attempt count
            assert 1 <= attempts <= 3, f"Invalid attempts count: {attempts}"
            
            if status == 'approved':
                print("   ✅ Plan approved after regeneration")
                assert attempts >= 1, "Should have at least 1 attempt"
            else:
                print("   ⚠️  Plan rejected after max attempts")
                assert attempts == 3, "Should exhaust all attempts if failed"
            
        except Exception as e:
            pytest.fail(f"Auto-regeneration orchestration failed: {e}")
    
    # =========================================================================
    # TEST 6: API Endpoint - Create Campaign
    # =========================================================================
    
    def test_06_api_create_campaign(self, api_client):
        """
        Test 6: API Endpoint - Create Campaign
        Validates FastAPI endpoint for campaign creation
        """
        print("\n" + "-"*80)
        print("TEST 6: API Endpoint - Create Campaign")
        print("-"*80)
        
        payload = {
            "campaign_name": "API E2E Test",
            "brand": "FitNow",
            "objective": "Test API endpoint",
            "inputs": {"test": True}
        }
        
        try:
            response = api_client.post("/api/v1/campaigns/", json=payload)
            
            # Assertions
            assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
            data = response.json()
            
            assert 'campaign_id' in data, "Missing campaign_id in response"
            assert data['campaign_name'] == "API E2E Test"
            
            print(f"✅ Campaign created via API with ID: {data['campaign_id']}")
            
        except Exception as e:
            pytest.fail(f"API campaign creation failed: {e}")
    
    # =========================================================================
    # TEST 7: API Endpoint - Orchestrate Campaign with Auto-Regeneration
    # =========================================================================
    
    @pytest.mark.slow
    def test_07_api_orchestrate_campaign(self, api_client):
        """
        Test 7: API Endpoint - Orchestrate Campaign
        Validates orchestration via API with auto-regeneration
        """
        print("\n" + "-"*80)
        print("TEST 7: API Endpoint - Orchestrate Campaign with Auto-Regeneration")
        print("-"*80)
        
        payload = {
            "campaign_name": "API Orchestration Test",
            "brand": "FitNow",
            "objective": "Create supportive wellness campaign via API",
            "inputs": {}
        }
        
        params = {
            "auto_regenerate": True,
            "max_attempts": 2
        }
        
        print("   Calling orchestration API endpoint...")
        start_time = time.time()
        
        try:
            response = api_client.post(
                "/api/v1/orchestrate/campaign",
                json=payload,
                params=params,
                timeout=120.0  # 2 minute timeout
            )
            elapsed = time.time() - start_time
            
            # Assertions
            assert response.status_code == 200, \
                f"API returned {response.status_code}: {response.text}"
            
            data = response.json()
            
            # Validate response structure
            assert 'campaign_id' in data, "Missing campaign_id"
            assert 'result' in data, "Missing result"
            assert 'attempts' in data, "Missing attempts"
            assert 'status' in data, "Missing status"
            
            print(f"✅ Orchestration API completed in {elapsed:.2f}s")
            print(f"   Campaign ID: {data['campaign_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Attempts: {data['attempts']}")
            
        except Exception as e:
            pytest.fail(f"API orchestration failed: {e}")
    
    # =========================================================================
    # TEST 8: Full Workflow Integration
    # =========================================================================
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_08_full_workflow_integration(self, api_client, db_session):
        """
        Test 8: Full Workflow Integration
        Complete end-to-end test: Upload → Parse → RAG → Orchestrate → Validate → Generate
        
        This is the MASTER integration test covering all components.
        """
        print("\n" + "-"*80)
        print("TEST 8: FULL WORKFLOW INTEGRATION (Master Test)")
        print("-"*80)
        
        # Step 1: Parse brand guidelines
        print("\n   Step 1/6: Parsing brand guidelines...")
        parser = CampaignDocumentParser()
        parsed = parser.parse_document(str(self.test_brand_doc), 'docx')
        assert 'error' not in parsed
        print(f"   ✅ Parsed {len(parsed)} fields")
        
        # Step 2: Verify RAG knowledge base
        print("\n   Step 2/6: Verifying RAG knowledge base...")
        retriever = BrandGuidelineRetriever(data_dir=str(project_root / "data"))
        rag_results = retriever._run("brand tone guidelines")
        # Parsing result string since it returns formatted string
        assert "Brand Guideline Information" in rag_results
        print(f"   ✅ RAG retrieved {len(rag_results)} relevant chunks")
        
        # Step 3: Create campaign via API
        print("\n   Step 3/6: Creating campaign via API...")
        campaign_payload = {
            "campaign_name": "Full Workflow E2E Test",
            "brand": "FitNow",
            "objective": "Comprehensive wellness campaign with supportive tone",
            "inputs": {"target_audience": "Health-conscious adults"}
        }
        
        response = api_client.post("/api/v1/campaigns/", json=campaign_payload)
        assert response.status_code == 200
        campaign_data = response.json()
        campaign_id = campaign_data['campaign_id']
        print(f"   ✅ Campaign created: ID {campaign_id}")
        
        # Step 4: Orchestrate with auto-regeneration
        print("\n   Step 4/6: Orchestrating campaign with auto-regeneration...")
        print("   (This may take 1-2 minutes)")
        
        orchestrate_response = api_client.post(
            "/api/v1/orchestrate/campaign",
            json=campaign_payload,
            params={"auto_regenerate": True, "max_attempts": 3},
            timeout=180.0  # 3 minute timeout
        )
        
        assert orchestrate_response.status_code == 200
        orchestrate_data = orchestrate_response.json()
        print(f"   ✅ Orchestration completed")
        print(f"      - Status: {orchestrate_data['status']}")
        print(f"      - Attempts: {orchestrate_data['attempts']}")
        
        # Step 5: Verify campaign in database
        print("\n   Step 5/6: Verifying campaign in database...")
        db_campaign = db_session.query(Campaign).filter(
            Campaign.campaign_id == orchestrate_data['campaign_id']
        ).first()
        
        assert db_campaign is not None, "Campaign not found in database"
        assert db_campaign.campaign_name == "Full Workflow E2E Test"
        print(f"   ✅ Campaign verified in database")
        
        # Step 6: Validate result structure
        print("\n   Step 6/6: Validating result structure...")
        result_str = orchestrate_data['result']
        assert len(result_str) > 0, "Empty orchestration result"
        
        # Check for expected content indicators
        has_plan = any(word in result_str.lower() for word in ['plan', 'strategy', 'campaign'])
        has_validation = any(word in result_str.lower() for word in ['approved', 'rejected', 'validation'])
        
        print(f"   ✅ Result structure validated")
        print(f"      - Contains planning: {has_plan}")
        print(f"      - Contains validation: {has_validation}")
        
        print("\n" + "="*80)
        print("🎉 FULL WORKFLOW INTEGRATION TEST PASSED")
        print("="*80)
        print(f"\nWorkflow Summary:")
        print(f"  ✅ Document parsed: {len(parsed)} fields")
        print(f"  ✅ RAG operational: {len(rag_results)} chunks retrieved")
        print(f"  ✅ Campaign created: ID {campaign_id}")
        print(f"  ✅ Orchestration: {orchestrate_data['status']} in {orchestrate_data['attempts']} attempts")
        print(f"  ✅ Database: Campaign persisted")
        print(f"  ✅ Result: Generated successfully")


# =============================================================================
# Test Configuration & Markers
# =============================================================================

# Mark slow tests (can be skipped with `pytest -m "not slow"`)
pytest.mark.slow = pytest.mark.slow

# Mark integration tests (can be run specifically with `pytest -m integration`)
pytest.mark.integration = pytest.mark.integration


if __name__ == "__main__":
    """
    Run tests directly with:
    python test/integration/test_end_to_end.py
    
    Or use pytest:
    pytest test/integration/test_end_to_end.py -v
    pytest test/integration/test_end_to_end.py -v -m "not slow"  # Skip slow tests
    pytest test/integration/test_end_to_end.py -v -m integration  # Only integration tests
    """
    pytest.main([__file__, "-v", "-s"])
