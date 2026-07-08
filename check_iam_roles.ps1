# Check Your IAM Roles in Google Cloud
# This script checks what IAM roles you have on the project

Write-Host "🔍 Checking Your IAM Roles on Google Cloud" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "sandbox-7940"

# Check if gcloud is installed
$gcloudInstalled = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudInstalled) {
    Write-Host "❌ gcloud CLI is not installed." -ForegroundColor Red
    Write-Host ""
    Write-Host "You can still check via the web console:" -ForegroundColor Yellow
    Write-Host "  https://console.cloud.google.com/iam-admin/iam?project=$PROJECT_ID" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To install gcloud CLI:" -ForegroundColor Yellow
    Write-Host "  Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ gcloud CLI found" -ForegroundColor Green
Write-Host ""

# Get current authenticated user
Write-Host "📋 Getting your account information..." -ForegroundColor Yellow
$CURRENT_USER = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null

if (-not $CURRENT_USER) {
    Write-Host "❌ No authenticated user found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please authenticate first:" -ForegroundColor Yellow
    Write-Host "  gcloud auth login" -ForegroundColor Cyan
    Write-Host "  gcloud auth application-default login" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Authenticated as: $CURRENT_USER" -ForegroundColor Green
Write-Host ""

# Get IAM policy for the project
Write-Host "🔐 Fetching IAM roles for project: $PROJECT_ID..." -ForegroundColor Yellow
Write-Host ""

try {
    # Get all IAM bindings for the user
    $iamPolicy = gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:$CURRENT_USER" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "📊 Your IAM Roles on project '$PROJECT_ID':" -ForegroundColor Cyan
        Write-Host "=============================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host $iamPolicy
        Write-Host ""
        
        # Check specifically for Vertex AI roles
        Write-Host "🔍 Checking for Vertex AI permissions..." -ForegroundColor Yellow
        $hasVertexAI = $iamPolicy -match "aiplatform"
        
        if ($hasVertexAI) {
            Write-Host "✅ You have Vertex AI related roles!" -ForegroundColor Green
        } else {
            Write-Host "❌ You don't have Vertex AI roles" -ForegroundColor Red
            Write-Host ""
            Write-Host "You need: roles/aiplatform.user" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "=============================================" -ForegroundColor Cyan
        
    } else {
        Write-Host "❌ Failed to get IAM policy" -ForegroundColor Red
        Write-Host "Error: $iamPolicy" -ForegroundColor Red
        Write-Host ""
        Write-Host "You may not have permission to view IAM policies." -ForegroundColor Yellow
        Write-Host "Ask your admin or check the web console:" -ForegroundColor Yellow
        Write-Host "  https://console.cloud.google.com/iam-admin/iam?project=$PROJECT_ID" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "❌ Error checking IAM roles: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "📱 Alternative: Check via Web Console" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open this URL in your browser:" -ForegroundColor Yellow
Write-Host "  https://console.cloud.google.com/iam-admin/iam?project=$PROJECT_ID" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then search for your email: $CURRENT_USER" -ForegroundColor Yellow
Write-Host ""

Write-Host "🎯 Required Role for Vertex AI:" -ForegroundColor Cyan
Write-Host "  • Vertex AI User (roles/aiplatform.user)" -ForegroundColor Yellow
Write-Host ""
