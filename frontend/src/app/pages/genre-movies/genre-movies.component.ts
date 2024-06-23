import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { GenreMovies } from '../../models/genre.model';

@Component({
  selector: 'app-genre-movies',
  templateUrl: './genre-movies.component.html',
  styleUrl: './genre-movies.component.css',
})
export class GenreMoviesComponent implements OnInit {
  slug: string = '';
  genre: GenreMovies | undefined;

  constructor(private route: ActivatedRoute, private api: ApiService) {}

  loadGenreMovies() {
    this.api.getGenreMovies(this.slug).subscribe({
      next: (data) => {
        this.genre = data;
      },
      error: (error) => {
        console.error("Can't request genres from api!", error);
      },
    });
  }

  ngOnInit(): void {
    this.slug = this.route.snapshot.params['slug'];
    this.loadGenreMovies();
  }
}
