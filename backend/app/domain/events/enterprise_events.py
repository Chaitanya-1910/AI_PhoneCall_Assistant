from app.domain.events.models import DomainEvent

class DeploymentStarted(DomainEvent):
    event_type: str = "DeploymentStarted"

class FailoverTriggered(DomainEvent):
    event_type: str = "FailoverTriggered"

class ComplianceReportGenerated(DomainEvent):
    event_type: str = "ComplianceReportGenerated"

class SecurityAlertRaised(DomainEvent):
    event_type: str = "SecurityAlertRaised"

class AIProviderChanged(DomainEvent):
    event_type: str = "AIProviderChanged"
