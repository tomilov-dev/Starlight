import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { Genre } from '../../models/genre.model';

@Component({
  selector: 'app-genres',
  templateUrl: './genres.component.html',
  styleUrl: './genres.component.css',
})
export class GenresComponent implements OnInit {
  genres: Genre[] = [];

  constructor(private dataService: DataService) {}

  ngOnInit() {
    this.loadGenres();
  }

  loadGenres() {
    this.genres = this.dataService.getGenres();
  }
}
