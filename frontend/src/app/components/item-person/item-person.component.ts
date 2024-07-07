import { Component, Input } from '@angular/core';
import { IMDbPersonBase } from '../../models/person.model';

@Component({
  selector: 'app-item-person',
  templateUrl: './item-person.component.html',
  styleUrl: './item-person.component.css',
})
export class ItemPersonComponent {
  @Input() person: IMDbPersonBase | undefined;
}
