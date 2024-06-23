import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomePageComponent } from './pages/home-page/home-page.component';
import { GenresComponent } from './pages/genres/genres.component';
import { SearchComponent } from './pages/search/search.component';
import { GenreMoviesComponent } from './pages/genre-movies/genre-movies.component';

const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'genres', component: GenresComponent },
  { path: 'genres/:slug', component: GenreMoviesComponent },
  { path: 'search', component: SearchComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
