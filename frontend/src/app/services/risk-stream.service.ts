import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject, Observable } from 'rxjs';
import { Alert, SystemStats, Transaction } from '../models/risk.models';

@Injectable({
  providedIn: 'root'
})
export class RiskStreamService {
  private readonly backendOrigin = this.resolveBackendOrigin();
  private readonly wsUrl = `${this.backendOrigin.replace(/^http/, 'ws')}/ws`;
  private readonly apiUrl = `${this.backendOrigin}/api`;
  private socket?: WebSocket;

  private alertsSubject = new BehaviorSubject<Alert[]>([]);
  public alerts$: Observable<Alert[]> = this.alertsSubject.asObservable();

  private transactionsSubject = new Subject<Transaction>();
  public transactions$: Observable<Transaction> = this.transactionsSubject.asObservable();

  private statsSubject = new BehaviorSubject<SystemStats>({
    totalProcessed: 0,
    totalAlerts: 0,
    activeFreezes: 0,
    preventedLossClp: 0,
    averageLatencyMs: 1.4,
    autopoiesisCycle: 1
  });
  public stats$: Observable<SystemStats> = this.statsSubject.asObservable();

  private isConnectedSubject = new BehaviorSubject<boolean>(false);
  public isConnected$: Observable<boolean> = this.isConnectedSubject.asObservable();

  constructor() {
    this.connect();
  }

  private resolveBackendOrigin(): string {
    const { hostname, origin, port, protocol } = window.location;
    if (port !== '4200') return origin;
    const backendProtocol = protocol === 'https:' ? 'https:' : 'http:';
    return `${backendProtocol}//${hostname}:8080`;
  }

  public connect(): void {
    try {
      this.socket = new WebSocket(this.wsUrl);

      this.socket.onopen = () => {
        console.log('[ShieldGuard] WebSocket conectado a motor Go');
        this.isConnectedSubject.next(true);
      };

      this.socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          this.handleIncomingMessage(msg);
        } catch (e) {
          console.error('[ShieldGuard] Error parseando mensaje WS:', e);
        }
      };

      this.socket.onclose = () => {
        console.log('[ShieldGuard] WebSocket desconectado. Reintentando en 3s...');
        this.isConnectedSubject.next(false);
        setTimeout(() => this.connect(), 3000);
      };

      this.socket.onerror = (error) => {
        console.warn('[ShieldGuard] WebSocket error (Go backend offline?):', error);
      };
    } catch (err) {
      console.error('[ShieldGuard] Excepción conectando socket:', err);
    }
  }

  private handleIncomingMessage(msg: { type: string; payload: any }): void {
    switch (msg.type) {
      case 'INITIAL_ALERTS':
        this.alertsSubject.next(msg.payload || []);
        break;

      case 'ALERT': {
        const current = this.alertsSubject.getValue();
        // Prepend new alert, keep list unique by id
        const filtered = current.filter(a => a.id !== msg.payload.id);
        this.alertsSubject.next([msg.payload, ...filtered]);
        break;
      }

      case 'TRANSACTION':
        this.transactionsSubject.next(msg.payload);
        break;

      case 'STATS':
        this.statsSubject.next(msg.payload);
        break;

      case 'CARD_FROZEN':
      case 'CARD_UNFROZEN':
        // Refresh alerts when status changes
        this.refreshAlerts();
        break;
    }
  }

  public async refreshAlerts(): Promise<void> {
    try {
      const res = await fetch(`${this.apiUrl}/alerts`);
      if (res.ok) {
        const data = await res.json();
        this.alertsSubject.next(data || []);
      }
    } catch (err) {
      console.warn('Error fetching alerts:', err);
    }
  }

  public async freezeCard(cardNumber: string, reason: string): Promise<boolean> {
    try {
      const res = await fetch(`${this.apiUrl}/cards/freeze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cardNumber,
          reason,
          operator: 'Mauricio Muñoz (Gerente Riesgo)'
        })
      });
      return res.ok;
    } catch (e) {
      console.error('Error freezing card:', e);
      return false;
    }
  }

  public async unfreezeCard(cardNumber: string): Promise<boolean> {
    try {
      const res = await fetch(`${this.apiUrl}/cards/unfreeze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cardNumber,
          operator: 'Mauricio Muñoz (Reversa Operacional)'
        })
      });
      return res.ok;
    } catch (e) {
      console.error('Error unfreezing card:', e);
      return false;
    }
  }

  public async injectScenario(scenario: string): Promise<'alerted' | 'blocked' | 'failed'> {
    try {
      const res = await fetch(`${this.apiUrl}/simulator/inject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario })
      });
      if (!res.ok) return 'failed';
      const result = await res.json();
      return result.alert ? 'alerted' : 'blocked';
    } catch (e) {
      console.error('Error injecting scenario:', e);
      return 'failed';
    }
  }

  public async getSimulatorStatus(): Promise<boolean | null> {
    try {
      const res = await fetch(`${this.apiUrl}/simulator/status`);
      if (!res.ok) return null;
      const data = await res.json();
      return data.running;
    } catch (e) {
      console.error('Error reading simulator status:', e);
      return null;
    }
  }

  public async toggleSimulator(): Promise<boolean | null> {
    try {
      const res = await fetch(`${this.apiUrl}/simulator/toggle`, { method: 'POST' });
      if (!res.ok) return null;
      const data = await res.json();
      return data.running;
    } catch (e) {
      console.error('Error toggling simulator:', e);
      return null;
    }
  }
}
