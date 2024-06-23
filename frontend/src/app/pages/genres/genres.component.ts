import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { Genre } from '../../models/genre.model';
import { throwError } from 'rxjs';

@Component({
  selector: 'app-genres',
  templateUrl: './genres.component.html',
  styleUrl: './genres.component.css',
})
export class GenresComponent implements OnInit {
  genres: Genre[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadGenres();
  }

  loadGenres() {
    this.api.getGenres().subscribe({
      next: (data) => {
        this.genres = data;
      },
      error: (error) => {
        console.error("Can't request genres from api!", error);
      },
    });
  }
}
