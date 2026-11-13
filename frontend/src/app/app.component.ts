import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { RiskStreamService } from './services/risk-stream.service';
import { Alert, SystemStats, Transaction } from './models/risk.models';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  public alerts: Alert[] = [];
  public stats: SystemStats = {
    totalProcessed: 0,
    totalAlerts: 0,
    activeFreezes: 0,
    preventedLossClp: 0,
    averageLatencyMs: 1.4,
    autopoiesisCycle: 1
  };
  public recentTransactions: Transaction[] = [];
  public isConnected = false;
  public selectedAlert?: Alert;
  public simulatorRunning = true;
  public actionMessage = '';

  private subs = new Subscription();

  constructor(private riskService: RiskStreamService) {}

  ngOnInit(): void {
    this.riskService.getSimulatorStatus().then(running => {
      if (running !== null) this.simulatorRunning = running;
    });

    this.subs.add(
      this.riskService.isConnected$.subscribe(conn => {
        this.isConnected = conn;
      })
    );

    this.subs.add(
      this.riskService.alerts$.subscribe(list => {
        const previousFirstId = this.alerts[0]?.id;
        this.alerts = list;
        if (list.length > 0 && (!this.selectedAlert || list[0].id !== previousFirstId)) {
          this.selectedAlert = list[0];
        } else if (this.selectedAlert) {
          const updated = list.find(a => a.id === this.selectedAlert!.id);
          this.selectedAlert = updated ?? list[0];
        }
      })
    );

    this.subs.add(
      this.riskService.stats$.subscribe(s => {
        this.stats = s;
      })
    );

    this.subs.add(
      this.riskService.transactions$.subscribe(tx => {
        this.recentTransactions.unshift(tx);
        if (this.recentTransactions.length > 6) {
          this.recentTransactions.pop();
        }
      })
    );
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  public selectAlert(alert: Alert): void {
    this.selectedAlert = alert;
  }

  public get prioritizedAlerts(): Alert[] {
    const latestByCard = new Map<string, Alert>();
    for (const alert of this.alerts) {
      if (!latestByCard.has(alert.cardNumber)) latestByCard.set(alert.cardNumber, alert);
    }
    return [...latestByCard.values()].sort((a, b) => b.riskScore.score - a.riskScore.score);
  }

  public get openAlertCount(): number {
    return new Set(
      this.alerts.filter(alert => alert.status === 'PENDIENTE').map(alert => alert.cardNumber)
    ).size;
  }

  public riskLabel(alert: Alert): string {
    return alert.riskScore.riskLevel === 'AUTOFRAUDE_PROBABLE' ? 'Riesgo alto' :
      alert.riskScore.riskLevel === 'REVISAR' ? 'Revisar' : 'Normal';
  }

  public statusLabel(status: Alert['status']): string {
    const labels: Record<Alert['status'], string> = {
      PENDIENTE: 'Pendiente',
      CONGELADO_PREVENTIVO: 'Congelada',
      REVERTIDO: 'Revertida',
      FRAUDE_CONFIRMADO: 'Fraude confirmado'
    };
    return labels[status];
  }

  public mlReasonLabel(code: string): string {
    const labels: Record<string, string> = {
      amount_above_customer_baseline: 'Monto superior al patrón de referencia',
      card_not_present_channel: 'Canal de compra no presencial',
      sensitive_merchant_category: 'Categoría de comercio sensible',
      rapid_location_change: 'Cambio de ubicación en poco tiempo',
      high_card_transaction_count: 'Conteo histórico alto para esta tarjeta'
    };
    return labels[code] ?? code;
  }

  public async freezeSelected(): Promise<void> {
    if (!this.selectedAlert) return;
    const card = this.selectedAlert.cardNumber;
    const ok = await this.riskService.freezeCard(card, 'Bloqueo Proactivo Preventivo Ley 20.009');
    if (ok) {
      this.showMessage(`Tarjeta ${card} congelada preventivamente antes del reclamo.`);
    } else {
      this.showMessage('No se pudo congelar la tarjeta. Comprueba la conexión con el motor.');
    }
  }

  public async unfreezeSelected(): Promise<void> {
    if (!this.selectedAlert) return;
    const card = this.selectedAlert.cardNumber;
    const ok = await this.riskService.unfreezeCard(card);
    if (ok) {
      this.showMessage(`Bloqueo revertido para tarjeta ${card} (Falso positivo calibrado).`);
    } else {
      this.showMessage('No se pudo revertir el congelamiento. Comprueba la conexión con el motor.');
    }
  }

  public async injectAttack(scenario: string): Promise<void> {
    const result = await this.riskService.injectScenario(scenario);
    const message = result === 'alerted' ? 'Escenario evaluado: se generó una alerta.' :
      result === 'blocked' ? 'Escenario evaluado: la tarjeta ya estaba congelada y no generó una alerta.' :
        'No se pudo enviar el escenario simulado.';
    this.showMessage(message);
  }

  public async toggleSimulator(): Promise<void> {
    const running = await this.riskService.toggleSimulator();
    if (running === null) {
      this.showMessage('No se pudo cambiar el estado del flujo. Comprueba la conexión con el motor.');
      return;
    }
    this.simulatorRunning = running;
    this.showMessage(running ? 'Flujo de prueba reanudado.' : 'Flujo de prueba pausado.');
  }

  public formatCLP(val: number): string {
    return '$' + val.toLocaleString('es-CL');
  }

  private showMessage(msg: string): void {
    this.actionMessage = msg;
    setTimeout(() => {
      if (this.actionMessage === msg) this.actionMessage = '';
    }, 4500);
  }
}
