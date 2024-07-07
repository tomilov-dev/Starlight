import { Component, Input } from '@angular/core';
import { IMDbMovieBase } from '../../models/base.movie.model';

@Component({
  selector: 'app-item-movie',
  templateUrl: './item-movie.component.html',
  styleUrl: './item-movie.component.css',
})
export class ItemMovieComponent {
  @Input() movie?: IMDbMovieBase;
}
